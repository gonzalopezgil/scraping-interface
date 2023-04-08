ENABLE_LINKS_JS = """
    var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
        links[i].removeEventListener("click", disableLink);
    }

    // Remove red background from previously painted elements
    for (var i = 0; i < redElements.length; i++) {
        redElements[i].style.backgroundColor = '';
    }
    redElements = [];

    // Remove all the squares created
    var squares = document.querySelectorAll('div[style*="2px solid red"]');
    squares.forEach(function(square) {
        square.parentNode.removeChild(square);
    });
"""

DISABLE_LINKS_JS = """
    var redElements = [];

    var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener("click", disableLink);
    }

    function disableLink(event) {
        event.preventDefault();
    }

    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th, div');
    for (var i = 0; i < textElements.length; i++) {
        textElements[i].addEventListener("click", scrapeData);
    }

    function scrapeData(event) {
        var selectedText = event.target.innerText.trim();
        if (selectedText) {
            console.log("selectedText: " + selectedText)

            // Get the XPath of the clicked element
            var xpathResult = document.evaluate(
                'ancestor-or-self::*',
                event.target,
                null,
                XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                null
            );
            var xpath = '';
            var divCount = 0;
            var i = xpathResult.snapshotLength - 1;
            while (divCount < 3 && i >= 0) {
                var element = xpathResult.snapshotItem(i);
                var tagName = element.tagName.toLowerCase();
                if (tagName === 'html' || tagName === 'body') {
                    xpath = '//' + tagName + xpath;
                } else {
                    var classes = '';
                    if (tagName === 'div') {
                        if (element.className) {
                            classes = '[contains(@class, "';
                            var classList = element.className.split(' ');
                            var j = 0;
                            while (j < classList.length && !/\d/.test(classList[j]) && classList[j] !== 'selected') {
                                if (j > 0) {
                                    classes += ' ';
                                }
                                classes += classList[j];
                                j++;
                            }
                            if (j === 0) {
                                classes = '';
                            } else {
                                classes += '")]';
                            }
                        }
                        divCount++;
                        xpath = '//' + tagName + classes + xpath;
                    } else {
                        divCount = 0;
                        if (i == xpathResult.snapshotLength - 1) {
                            var index = getElementIndex(element);
                            xpath = '//' + tagName + '[' + index + ']' + xpath;
                        } else {
                            xpath = '//' + tagName + xpath;
                        }
                    }
                }
                i--;
            }
            console.log(xpath);

            var elements = document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);  // Find all elements that match the XPath
            var count = 0;
            var element = elements.iterateNext();
            while (element) {
                count++;
                element.style.backgroundColor = 'red';  // Paint the element with a red background color
                redElements.push(element);
                element = elements.iterateNext();
            }
            console.log(count);
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
