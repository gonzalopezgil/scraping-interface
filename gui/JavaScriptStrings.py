ENABLE_LINKS_JS = """
        var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
        links[i].removeEventListener("click", disableLink);
    }
"""

# The last part is from HIGHLIGHT_TEXT_JS
DISABLE_LINKS_JS = """
    var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener("click", disableLink);
    }

    function disableLink(event) {
        event.preventDefault();
    }

    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th');
    for (var i = 0; i < textElements.length; i++) {
        textElements[i].addEventListener("click", copyToClipboard);
    }

    function copyToClipboard(event) {
        var selectedText = event.target.innerText.trim();
        if (selectedText) {
            var textarea = document.createElement("textarea");
            document.body.appendChild(textarea);
            textarea.value = selectedText;
            textarea.select();
            document.execCommand("copy");
            document.body.removeChild(textarea);

            var style = document.createElement('style');
            document.head.appendChild(style);
            var range = document.createRange();
            range.selectNodeContents(document.body);
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        }
    }
"""


HIGHLIGHT_TEXT_JS = """
    var style = document.createElement('style');
    document.head.appendChild(style);
    var range = document.createRange();
    range.selectNodeContents(document.body);
    var selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);

    var preventMousedown = function(event) {
        event.preventDefault();
    };

    document.addEventListener('mousedown', preventMousedown);
"""

UNHIGHLIGHT_TEXT_JS = """
    var selection = window.getSelection();
    selection.removeAllRanges();
    document.removeEventListener('mousedown', preventMousedown);
"""

# Unused
FULL_DIV_JS = """
    var overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(255, 255, 255, 0)';
    document.body.appendChild(overlay);
"""

# Unused
COLOR_TEXT_JS = """
    var style = document.createElement('style');
    style.innerHTML = '* { color: yellow !important; }';
    document.head.appendChild(style);
"""
