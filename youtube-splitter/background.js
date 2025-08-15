chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'splitVideo') {
    (async () => {
      try {
        console.log('Received splitVideo message with URL:', request.url);
        const response = await fetch('http://localhost:5000/split', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: request.url })
        });
        const data = await response.json();
        if (data.success) {
          console.log('Splitting video succeeded, downloading zip...');
          chrome.downloads.download(
            { url: data.downloadUrl, filename: 'split_videos.zip' },
            downloadId => {
              console.log('Download started with ID:', downloadId);
            }
          );
          sendResponse({ success: true });
        } else {
          console.error('Failed to split video:', data.error);
          sendResponse({ success: false, error: data.error });
        }
      } catch (error) {
        console.error('Error:', error);
        sendResponse({ success: false, error: error.toString() });
      }
    })();
    return true; // Keep the message channel open for sendResponse
  }
});
