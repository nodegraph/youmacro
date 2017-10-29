package com.youmacro.javawebview;

import android.graphics.Bitmap;
import android.util.Log;
import android.view.View;
import android.webkit.WebView;
import android.webkit.WebViewClient;


import java.lang.String;

// A WebViewClient implementation which forwards events to another
// listener object. 
public class ForwardingWebViewClient extends WebViewClient{

  WebViewEventsListenerInterface _listener;

  public ForwardingWebViewClient(WebViewEventsListenerInterface listener){
    super();
    this._listener = listener;
  }

  @Override
  public boolean shouldOverrideUrlLoading(WebView view, String url){
    this._listener.shouldOverrideUrlLoading(view,url);
    return false;
  }

  @Override
  public void onPageStarted(WebView view, String url, Bitmap favicon){
    this._listener.onPageStarted(view,url,favicon);
  }

  @Override
  public void onPageFinished(WebView view, String url){
    this._listener.onPageFinished(view,url);
  }

  public void onPageCommitVisible(WebView view, String url){
    this._listener.onPageCommitVisible(view,url);
  }

  @Override
  public void onReceivedError(WebView view, int errorCode, String description, String failingUrl){
    this._listener.onReceivedError(view, errorCode, description, failingUrl);
  }

} 


