package com.youmacro.javawebview;

import android.graphics.Bitmap;
import android.webkit.WebView;

import java.lang.String;

public interface WebViewEventsListenerInterface{

    public void shouldOverrideUrlLoading(WebView view, String url);

    public void onPageStarted(WebView view, String url, Bitmap favicon);

    public void onPageFinished(WebView view, String url);

    public void onPageCommitVisible(WebView view, String url);

    public void onReceivedError(WebView view,  int errorCode, String description, String failingUrl);

    public void onBackButton(WebView view);
}

