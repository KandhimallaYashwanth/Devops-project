function initializeGoogleTranslate() {
    new google.translate.TranslateElement({
      pageLanguage: 'en', 
      includedLanguages: 'en,te,hi,ta,ma,ka,be,or,pa,sa', 
      layout: google.translate.TranslateElement.InlineLayout.SIMPLE
    }, 'google_translate_element');
  }
  
  // Ensure the translate script is loaded before initialization
  function loadGoogleTranslateScript() {
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = 'https://translate.google.com/translate_a/element.js?cb=initializeGoogleTranslate';
    document.head.appendChild(script);
  }
  
  // Add translate element to page if not already present
  function ensureTranslateElementExists() {
    if (!document.getElementById('google_translate_element')) {
      const translateDiv = document.createElement('div');
      translateDiv.id = 'google_translate_element';
      translateDiv.style.display = 'inline-block';
      translateDiv.style.position = 'fixed';
      translateDiv.style.top = '10px';
      translateDiv.style.right = '10px';
      
      // Add to body if no specific placement is needed
      document.body.appendChild(translateDiv);
    }
  }
  
  // Run on page load
  window.addEventListener('DOMContentLoaded', () => {
    ensureTranslateElementExists();
    loadGoogleTranslateScript();
  });
