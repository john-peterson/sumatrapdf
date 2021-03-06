/* Copyright 2013 the SumatraPDF project authors (see AUTHORS file).
   License: Simplified BSD (see COPYING.BSD) */
#ifndef HtmlWindow_h
#define HtmlWindow_h

#include <exdisp.h>

class FrameSite;
class HtmlMoniker;

// HtmlWindowCallback allows HtmlWindow to notify other code about notable
// events or delegate some of the functionality.
class HtmlWindowCallback
{
public:
    // called when we're about to show a given url. Returning false will
    // stop loading this url
    virtual bool OnBeforeNavigate(const WCHAR *url, bool newWindow) = 0;

    // called after html document has been completely loaded
    virtual void OnDocumentComplete(const WCHAR *url) = 0;

    // allows for providing data for a given url.
    // returning false means data wasn't provided.
    virtual bool GetDataForUrl(const WCHAR *url, char **data, size_t *len) = 0;

    // called when left mouse button is clicked in the web control window.
    // we use it to maintain proper focus (since it's stolen by left click)
    virtual void OnLButtonDown() = 0;
};

// HtmlWindow embeds a web browser (Internet Explorer) control
// inside provided HWND so that an app can display html content.
class HtmlWindow
{
protected:
    friend class FrameSite;

    int                 windowId;
    HWND                hwndParent;
    IWebBrowser2 *      webBrowser;
    IOleObject *        oleObject;
    IOleInPlaceObject * oleInPlaceObject;
    IViewObject *       viewObject;
    IConnectionPoint *  connectionPoint;
    HtmlMoniker *       htmlContent;
    HWND                oleObjectHwnd;

    DWORD               adviseCookie;
    bool                blankWasShown;

    ScopedMem<WCHAR>    currentURL;

    HtmlWindow(HWND hwndParent, HtmlWindowCallback *cb);

    void NavigateToAboutBlank();
    bool CreateBrowser();

    void SubclassHwnd();
    void UnsubclassHwnd();

public:
    ~HtmlWindow();

    void OnSize(SizeI size);
    void SetVisible(bool visible);
    void NavigateToUrl(const WCHAR *url);
    void NavigateToDataUrl(const WCHAR *url);
    void SetHtml(const char *s, size_t len=-1);
    void GoBack();
    void GoForward();
    void PrintCurrentPage();
    void SetZoomPercent(int zoom);
    int  GetZoomPercent();
    void FindInCurrentPage();
    void SelectAll();
    void CopySelection();
    LRESULT SendMsg(UINT msg, WPARAM wp, LPARAM lp);
    void OnLButtonDown() const;

    HBITMAP TakeScreenshot(RectI area, SizeI finalSize);
    bool    OnBeforeNavigate(const WCHAR *url, bool newWindow);
    void    OnDocumentComplete(const WCHAR *url);
    HRESULT OnDragEnter(IDataObject *dataObj);
    HRESULT OnDragDrop(IDataObject *dataObj);

    bool canGoBack;
    bool canGoForward;

    // TODO: not for public use
    WNDPROC wndProcBrowserPrev;
    HtmlWindowCallback *htmlWinCb;

    static HtmlWindow *Create(HWND hwndParent, HtmlWindowCallback *cb);
};

#endif
