package com.brasilfut.app;

import android.app.Activity;
import android.graphics.Bitmap;
import android.os.Build;
import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        );

        webView = new WebView(this);
        setContentView(webView);

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowFileAccessFromFileURLs(true);
        s.setAllowUniversalAccessFromFileURLs(true);
        s.setDomStorageEnabled(true);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setRenderPriority(WebSettings.RenderPriority.HIGH);
        s.setLayoutAlgorithm(WebSettings.LayoutAlgorithm.NARROW_COLUMNS);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT) {
            WebView.setWebContentsDebuggingEnabled(true);
        }

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                showError("Erro ao carregar: " + description);
            }

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
            }
        });

        webView.setWebChromeClient(new WebChromeClient());

        webView.loadUrl("file:///android_asset/brasil-fut.html");
    }

    private void showError(String msg) {
        final String error = msg.replace("'", "\\'");
        webView.post(() -> {
            String js = "document.body.innerHTML="
                + "'<div style=\"display:flex;align-items:center;justify-content:center;height:100vh;background:#060A0F;color:#EDF2F7;font-family:sans-serif;text-align:center;padding:40px\">"
                + "<div><h2 style=\"color:#FF4757;margin-bottom:16px\">Erro</h2>"
                + "<p style=\"color:#94A3B8;margin-bottom:24px\">" + error + "</p>"
                + "<button onclick=\"location.reload()\" style=\"padding:10px 24px;border:none;border-radius:8px;background:#00D166;color:#000;font-weight:600;font-size:14px\">Tentar novamente</button>"
                + "</div></div>';";
            webView.evaluateJavascript(js, null);
        });
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
