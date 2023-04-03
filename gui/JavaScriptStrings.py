ENABLE_LINKS_JS = """
    var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
        links[i].removeEventListener("click", disableLink);
    }

    // Remove all the squares created
    var squares = document.querySelectorAll('div[style*="2px solid red"]');
    squares.forEach(function(square) {
        square.parentNode.removeChild(square);
    });
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

    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th, div');
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

            var rangeText = document.createRange();
            rangeText.selectNodeContents(event.target);

            // create a new element and position it around the selected text
            var rect = rangeText.getBoundingClientRect();
            var square = document.createElement('div');
            square.style.position = 'absolute';
            square.style.left = rect.left + window.pageXOffset + 'px'; // adjust for page scroll
            square.style.top = rect.top + window.pageYOffset + 'px'; // adjust for page scroll
            square.style.width = rect.width + 'px';
            square.style.height = rect.height + 'px';
            square.style.border = '2px solid red';
            document.body.appendChild(square);

            // Get the XPath of the clicked element
            var xpathResult = document.evaluate(
                'ancestor-or-self::*',
                event.target,
                null,
                XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                null
            );
            var xpath = '';
            for (var i = 0; i < xpathResult.snapshotLength; i++) {
                var element = xpathResult.snapshotItem(i);
                var tagName = element.tagName.toLowerCase();
                var index = getElementIndex(element);
                var id = element.id ? '[@id="' + element.id + '"]' : '';
                var classes = element.className ? '[@class="' + element.className + '"]' : '';
                xpath += '/' + tagName + '[' + index + ']' + id + classes;
            }
            console.log(xpath);
        }
    }

    // Helper function to get the index of an element among its siblings
    function getElementIndex(element) {
        var index = 1;
        var sibling = element.previousSibling;
        while (sibling) {
            if (sibling.nodeType == 1 && sibling.tagName == element.tagName) {
                index++;
            }
            sibling = sibling.previousSibling;
        }
        return index;
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
