package com.aptari.mensajeapedido;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.media.AudioFormat;
import android.media.MediaCodec;
import android.media.MediaExtractor;
import android.media.MediaFormat;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.json.JSONArray;
import org.json.JSONObject;
import org.vosk.LibVosk;
import org.vosk.LogLevel;
import org.vosk.Model;
import org.vosk.Recognizer;
import org.vosk.android.StorageService;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final int REQ_AUDIO = 401;
    private static final int TARGET_RATE = 16000;
    private static final long CODEC_TIMEOUT_US = 10000;

    private WebView webView;
    private volatile Model model;
    private volatile boolean modelReady = false;
    private volatile boolean pageReady = false;
    private volatile Uri pendingAudio;
    private volatile String pendingAudioName;
    private Intent pendingShareIntent;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        LibVosk.setLogLevel(LogLevel.WARNINGS);

        webView = new WebView(this);
        setContentView(webView);
        configureWebView();
        pendingShareIntent = getIntent();
        initModel();
        webView.loadUrl("file:///android_asset/index.html");
    }

    private void configureWebView() {
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(false);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setGeolocationEnabled(false);
        s.setMediaPlaybackRequiresUserGesture(true);
        webView.addJavascriptInterface(new NativeBridge(), "AptariNative");
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return true;
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return true;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                pageReady = true;
                notifyModelState();
                consumeShareIntent();
            }
        });
    }

    private void initModel() {
        notifyStatus("Preparando reconocimiento de audio…");
        StorageService.unpack(this, "model-es", "model-es",
                unpacked -> {
                    model = unpacked;
                    modelReady = true;
                    runOnUiThread(() -> {
                        notifyModelState();
                        if (pendingAudio != null) {
                            Uri uri = pendingAudio;
                            String name = pendingAudioName;
                            pendingAudio = null;
                            pendingAudioName = null;
                            transcribeAudio(uri, name);
                        }
                    });
                },
                exception -> runOnUiThread(() -> notifyError(
                        "No se pudo preparar el reconocimiento de audio: " + safeMessage(exception))));
    }

    private void consumeShareIntent() {
        if (!pageReady || pendingShareIntent == null) return;
        Intent intent = pendingShareIntent;
        pendingShareIntent = null;
        if (!Intent.ACTION_SEND.equals(intent.getAction())) return;

        String type = intent.getType() == null ? "" : intent.getType();
        if (type.startsWith("text/")) {
            CharSequence shared = intent.getCharSequenceExtra(Intent.EXTRA_TEXT);
            if (shared != null && shared.length() > 0) {
                js("window.Aptari && window.Aptari.onSharedText(" + JSONObject.quote(shared.toString()) + ");");
            }
            return;
        }

        if (type.startsWith("audio/") || type.equals("application/ogg") || type.equals("application/octet-stream")) {
            Uri uri = intent.getParcelableExtra(Intent.EXTRA_STREAM);
            if (uri != null) queueOrTranscribe(uri, displayName(uri));
        }
    }

    private void notifyModelState() {
        if (!pageReady) return;
        String state = modelReady ? "ready" : "loading";
        js("window.Aptari && window.Aptari.onModelState(" + JSONObject.quote(state) + ");");
    }

    private void notifyStatus(String message) {
        if (!pageReady) return;
        js("window.Aptari && window.Aptari.onNativeStatus(" + JSONObject.quote(message) + ");");
    }

    private void notifyError(String message) {
        if (!pageReady) return;
        js("window.Aptari && window.Aptari.onNativeError(" + JSONObject.quote(message) + ");");
    }

    private void js(String script) {
        if (webView == null) return;
        runOnUiThread(() -> webView.evaluateJavascript(script, null));
    }

    private String safeMessage(Throwable t) {
        if (t == null || t.getMessage() == null || t.getMessage().trim().isEmpty()) return "error desconocido";
        return t.getMessage();
    }

    private void queueOrTranscribe(Uri uri, String name) {
        if (uri == null) return;
        if (!modelReady) {
            pendingAudio = uri;
            pendingAudioName = name;
            notifyStatus("Audio recibido. Esperando que termine de cargar el modelo de voz…");
            js("window.Aptari && window.Aptari.onAudioPicked(" + JSONObject.quote(name) + ", 'waiting');");
        } else {
            transcribeAudio(uri, name);
        }
    }

    private void transcribeAudio(Uri uri, String name) {
        js("window.Aptari && window.Aptari.onAudioPicked(" + JSONObject.quote(name) + ", 'processing');");
        notifyStatus("Transcribiendo audio en el teléfono…");
        executor.execute(() -> {
            try {
                byte[] pcm16k = decodeToPcm16Mono16k(uri);
                TranscriptResult result = recognize(pcm16k);
                if (result.text.trim().isEmpty()) {
                    throw new IOException("No se reconoció voz suficiente en el audio.");
                }
                String script = "window.Aptari && window.Aptari.onTranscriptReady(" +
                        JSONObject.quote(result.text) + "," +
                        JSONObject.quote(name) + "," +
                        String.format(java.util.Locale.US, "%.3f", result.confidence) + ");";
                js(script);
            } catch (Exception e) {
                notifyError("No pude transcribir este audio: " + safeMessage(e));
                js("window.Aptari && window.Aptari.onAudioFailed();");
            }
        });
    }

    private TranscriptResult recognize(byte[] pcm) throws IOException {
        if (model == null) throw new IOException("El modelo de voz todavía no está listo.");
        StringBuilder text = new StringBuilder();
        double confSum = 0.0;
        int confCount = 0;
        try (Recognizer recognizer = new Recognizer(model, TARGET_RATE)) {
            recognizer.setWords(true);
            final int chunk = 4096;
            for (int off = 0; off < pcm.length; off += chunk) {
                int len = Math.min(chunk, pcm.length - off);
                byte[] part = new byte[len];
                System.arraycopy(pcm, off, part, 0, len);
                if (recognizer.acceptWaveForm(part, len)) {
                    ParsedResult parsed = parseVosk(recognizer.getResult());
                    appendText(text, parsed.text);
                    confSum += parsed.confSum;
                    confCount += parsed.confCount;
                }
            }
            ParsedResult parsed = parseVosk(recognizer.getFinalResult());
            appendText(text, parsed.text);
            confSum += parsed.confSum;
            confCount += parsed.confCount;
        }
        double confidence = confCount == 0 ? 0.0 : confSum / confCount;
        return new TranscriptResult(text.toString().replaceAll("\\s+", " ").trim(), confidence);
    }

    private void appendText(StringBuilder sb, String part) {
        if (part == null || part.trim().isEmpty()) return;
        if (sb.length() > 0) sb.append(' ');
        sb.append(part.trim());
    }

    private ParsedResult parseVosk(String json) {
        ParsedResult out = new ParsedResult();
        try {
            JSONObject obj = new JSONObject(json);
            out.text = obj.optString("text", "");
            JSONArray words = obj.optJSONArray("result");
            if (words != null) {
                for (int i = 0; i < words.length(); i++) {
                    JSONObject w = words.optJSONObject(i);
                    if (w != null && w.has("conf")) {
                        out.confSum += w.optDouble("conf", 0.0);
                        out.confCount++;
                    }
                }
            }
        } catch (Exception ignored) {}
        return out;
    }

    private byte[] decodeToPcm16Mono16k(Uri uri) throws IOException {
        MediaExtractor extractor = new MediaExtractor();
        MediaCodec decoder = null;
        ByteArrayOutputStream rawOut = new ByteArrayOutputStream();
        int sampleRate = 0;
        int channels = 0;
        int pcmEncoding = AudioFormat.ENCODING_PCM_16BIT;

        try {
            extractor.setDataSource(this, uri, null);
            int audioTrack = -1;
            MediaFormat inputFormat = null;
            for (int i = 0; i < extractor.getTrackCount(); i++) {
                MediaFormat f = extractor.getTrackFormat(i);
                String mime = f.getString(MediaFormat.KEY_MIME);
                if (mime != null && mime.startsWith("audio/")) {
                    audioTrack = i;
                    inputFormat = f;
                    break;
                }
            }
            if (audioTrack < 0 || inputFormat == null) throw new IOException("El archivo no contiene una pista de audio reconocible.");

            extractor.selectTrack(audioTrack);
            String mime = inputFormat.getString(MediaFormat.KEY_MIME);
            if (mime == null) throw new IOException("Formato de audio no reconocido.");

            if (android.os.Build.VERSION.SDK_INT >= 24) {
                inputFormat.setInteger(MediaFormat.KEY_PCM_ENCODING, AudioFormat.ENCODING_PCM_16BIT);
            }

            decoder = MediaCodec.createDecoderByType(mime);
            decoder.configure(inputFormat, null, null, 0);
            decoder.start();

            boolean inputDone = false;
            boolean outputDone = false;
            MediaCodec.BufferInfo info = new MediaCodec.BufferInfo();

            while (!outputDone) {
                if (!inputDone) {
                    int inIndex = decoder.dequeueInputBuffer(CODEC_TIMEOUT_US);
                    if (inIndex >= 0) {
                        ByteBuffer input = decoder.getInputBuffer(inIndex);
                        if (input != null) {
                            input.clear();
                            int size = extractor.readSampleData(input, 0);
                            if (size < 0) {
                                decoder.queueInputBuffer(inIndex, 0, 0, 0, MediaCodec.BUFFER_FLAG_END_OF_STREAM);
                                inputDone = true;
                            } else {
                                long pts = extractor.getSampleTime();
                                decoder.queueInputBuffer(inIndex, 0, size, pts, 0);
                                extractor.advance();
                            }
                        }
                    }
                }

                int outIndex = decoder.dequeueOutputBuffer(info, CODEC_TIMEOUT_US);
                if (outIndex == MediaCodec.INFO_OUTPUT_FORMAT_CHANGED) {
                    MediaFormat outFormat = decoder.getOutputFormat();
                    if (outFormat.containsKey(MediaFormat.KEY_SAMPLE_RATE)) sampleRate = outFormat.getInteger(MediaFormat.KEY_SAMPLE_RATE);
                    if (outFormat.containsKey(MediaFormat.KEY_CHANNEL_COUNT)) channels = outFormat.getInteger(MediaFormat.KEY_CHANNEL_COUNT);
                    if (android.os.Build.VERSION.SDK_INT >= 24 && outFormat.containsKey(MediaFormat.KEY_PCM_ENCODING)) {
                        pcmEncoding = outFormat.getInteger(MediaFormat.KEY_PCM_ENCODING);
                    }
                } else if (outIndex >= 0) {
                    ByteBuffer output = decoder.getOutputBuffer(outIndex);
                    if (output != null && info.size > 0) {
                        if (pcmEncoding != AudioFormat.ENCODING_PCM_16BIT) {
                            throw new IOException("El decodificador entregó un PCM no compatible.");
                        }
                        output.position(info.offset);
                        output.limit(info.offset + info.size);
                        byte[] buf = new byte[info.size];
                        output.get(buf);
                        rawOut.write(buf, 0, buf.length);
                        if (rawOut.size() > 120 * 1024 * 1024) throw new IOException("El audio es demasiado largo para esta prueba.");
                    }
                    outputDone = (info.flags & MediaCodec.BUFFER_FLAG_END_OF_STREAM) != 0;
                    decoder.releaseOutputBuffer(outIndex, false);
                }
            }

            if (sampleRate <= 0 && inputFormat.containsKey(MediaFormat.KEY_SAMPLE_RATE)) sampleRate = inputFormat.getInteger(MediaFormat.KEY_SAMPLE_RATE);
            if (channels <= 0 && inputFormat.containsKey(MediaFormat.KEY_CHANNEL_COUNT)) channels = inputFormat.getInteger(MediaFormat.KEY_CHANNEL_COUNT);
            if (sampleRate <= 0 || channels <= 0) throw new IOException("No pude determinar la frecuencia o los canales del audio.");

            return convertPcm(rawOut.toByteArray(), sampleRate, channels);
        } finally {
            try { extractor.release(); } catch (Exception ignored) {}
            if (decoder != null) {
                try { decoder.stop(); } catch (Exception ignored) {}
                try { decoder.release(); } catch (Exception ignored) {}
            }
        }
    }

    private byte[] convertPcm(byte[] raw, int sourceRate, int channels) throws IOException {
        if (raw.length < 2) throw new IOException("El audio está vacío.");
        int totalShorts = raw.length / 2;
        int frames = totalShorts / channels;
        if (frames <= 0) throw new IOException("El audio no contiene muestras suficientes.");

        ByteBuffer bb = ByteBuffer.wrap(raw).order(ByteOrder.LITTLE_ENDIAN);
        short[] mono = new short[frames];
        for (int frame = 0; frame < frames; frame++) {
            int sum = 0;
            for (int ch = 0; ch < channels; ch++) sum += bb.getShort();
            mono[frame] = (short) (sum / channels);
        }

        short[] target;
        if (sourceRate == TARGET_RATE) {
            target = mono;
        } else {
            int outLen = Math.max(1, (int) Math.round(mono.length * (TARGET_RATE / (double) sourceRate)));
            target = new short[outLen];
            double ratio = sourceRate / (double) TARGET_RATE;
            for (int i = 0; i < outLen; i++) {
                double pos = i * ratio;
                int left = (int) Math.floor(pos);
                int right = Math.min(left + 1, mono.length - 1);
                double frac = pos - left;
                if (left >= mono.length) left = mono.length - 1;
                double value = mono[left] * (1.0 - frac) + mono[right] * frac;
                target[i] = (short) Math.max(Short.MIN_VALUE, Math.min(Short.MAX_VALUE, Math.round(value)));
            }
        }

        ByteBuffer out = ByteBuffer.allocate(target.length * 2).order(ByteOrder.LITTLE_ENDIAN);
        for (short s : target) out.putShort(s);
        return out.array();
    }

    private String displayName(Uri uri) {
        String result = "audio compartido";
        if (uri == null) return result;
        try (Cursor cursor = getContentResolver().query(uri, new String[]{OpenableColumns.DISPLAY_NAME}, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (idx >= 0) {
                    String name = cursor.getString(idx);
                    if (name != null && !name.trim().isEmpty()) result = name;
                }
            }
        } catch (Exception ignored) {}
        return result;
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        pendingShareIntent = intent;
        consumeShareIntent();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQ_AUDIO && resultCode == RESULT_OK && data != null && data.getData() != null) {
            Uri uri = data.getData();
            try {
                getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
            } catch (Exception ignored) {}
            queueOrTranscribe(uri, displayName(uri));
        }
    }

    @Override
    protected void onDestroy() {
        executor.shutdownNow();
        if (model != null) {
            try { model.close(); } catch (Exception ignored) {}
            model = null;
        }
        if (webView != null) {
            webView.removeJavascriptInterface("AptariNative");
            webView.destroy();
        }
        super.onDestroy();
    }

    @SuppressWarnings("deprecation")
    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    private static class ParsedResult {
        String text = "";
        double confSum = 0.0;
        int confCount = 0;
    }

    private static class TranscriptResult {
        final String text;
        final double confidence;
        TranscriptResult(String text, double confidence) {
            this.text = text;
            this.confidence = confidence;
        }
    }

    public class NativeBridge {
        @JavascriptInterface
        public void pickAudio() {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("audio/*");
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
                startActivityForResult(intent, REQ_AUDIO);
            });
        }

        @JavascriptInterface
        public void copyText(String text) {
            runOnUiThread(() -> {
                ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                cm.setPrimaryClip(ClipData.newPlainText("Pedido APTARI", text == null ? "" : text));
                js("window.Aptari && window.Aptari.onCopied();");
            });
        }

        @JavascriptInterface
        public String modelState() {
            return modelReady ? "ready" : "loading";
        }
    }
}
