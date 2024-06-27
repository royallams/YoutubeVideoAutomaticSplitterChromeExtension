console.log("Content script loaded");

function addButton() {
  console.log("addButton called");
  
  // Check if the button already exists
  if (document.getElementById('split-video-button')) {
    console.log("Button already exists");
    return;
  }

  // Create the button
  let button = document.createElement('button');
  button.id = 'split-video-button';
  button.innerText = 'Split Video';
  button.style.margin = '10px';
  button.style.padding = '10px';
  button.style.backgroundColor = '#ff0000';
  button.style.color = '#ffffff';
  button.style.border = 'none';
  button.style.cursor = 'pointer';

  // Wait for the target element to be available
  const intervalId = setInterval(() => {
    console.log("Checking for target element...");
    let target = document.querySelector('#top-level-buttons-computed');
    if (target) {
      console.log("Target element found!");
      clearInterval(intervalId);
      target.appendChild(button);

      // Add click event listener to the button
      button.addEventListener('click', () => {
        let videoUrl = window.location.href;
        console.log("Button clicked, URL:", videoUrl);
        chrome.runtime.sendMessage({ action: 'splitVideo', url: videoUrl }, response => {
          console.log('Response from background:', response);
        });
      });
    }
  }, 1000); // Check every second
}

// Add the button when the page loads
window.addEventListener('yt-navigate-finish', addButton);

// Add the button when navigating between videos
document.addEventListener('DOMContentLoaded', addButton);
