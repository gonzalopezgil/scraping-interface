ENABLE_LINKS_JS = """
    document.body.removeEventListener("click", disableLink);

    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th, div, button, img, input[type=button], input[type=submit], input[type=image], label, area, summary, svg, path, circle, rect');
    for (var i = 0; i < textElements.length; i++) {
        textElements[i].removeEventListener("click", disableLink);
        textElements[i].removeEventListener("click", scrapeData);
    }

    // Remove red background from previously painted elements
    for (var i = 0; i < redElements.length; i++) {
        redElements[i].style.backgroundColor = '';
    }
    redElements = [];

    // Remove green background from previously painted elements
    for (var i = 0; i < greenElements.length; i++) {
        greenElements[i].style.backgroundColor = '';
    }
    greenElements = [];

    // Remove all the squares created
    var squares = document.querySelectorAll('div[style*="2px solid red"]');
    squares.forEach(function(square) {
        square.parentNode.removeChild(square);
    });
"""

DISABLE_LINKS_JS = """
    document.body.addEventListener("click", disableLink);

    function disableLink(event) {
        event.stopPropagation();
        event.preventDefault();
    }

    highlightText();

    var lastMessage = "";
    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th, div, button, img, input[type=button], input[type=submit], input[type=image], label, area, summary, svg, path, circle, rect');
    for (var i = 0; i < textElements.length; i++) {
        textElements[i].addEventListener("click", disableLink);
        textElements[i].addEventListener("click", scrapeData);
    }

    document.addEventListener('mousedown', preventMousedown);
"""

START_JS = """
    var redElements = [];
    var greenElements = [];

    function highlightText() {
        var style = document.createElement('style');
        style.innerHTML = `
            ::selection {
                background: #E7d5ff; /* WebKit/Blink Browsers */
                color: black;
            }
            ::-moz-selection {
                background: #E7d5ff; /* Gecko Browsers */
                color: black;
            }
        `;
        document.head.appendChild(style);
        var range = document.createRange();
        range.selectNodeContents(document.body);
        var selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
    }

    function paintElementGreen(event) {
        highlightText();

        var clickedElement = event.target;
        clickedElement.style.backgroundColor = 'green';
        greenElements.push(clickedElement);

        var xpathResult = document.evaluate(
            'ancestor-or-self::*',
            clickedElement,
            null,
            XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
            null
        );
        var xpath = '';
        var skipClasses = false; // flag to skip classes for ancestors
        for (var i = xpathResult.snapshotLength - 1; i >= 0; i--) {
            var element = xpathResult.snapshotItem(i);
            var tagName = element.tagName.toLowerCase();
            var classes = '';
            var id = '';
            var text = '';
            var rel = '';
            var label = '';
            var ariaLabel = '';

            // If the element has an ID, use it and skip classes
            if (element.id) {
                id = '[@id="' + element.id + '"]';
                if (i == xpathResult.snapshotLength - 1) {
                    skipClasses = true;
                }
            } else if (i == xpathResult.snapshotLength - 1 && element.getAttribute('rel') === 'next') {
                // If the last element has a rel="next" attribute, add it and skip the rest
                rel = '[@rel="next"]';
                skipClasses = true;
            } else if (element.textContent && tagName !== 'html' && tagName !== 'body' && i == xpathResult.snapshotLength - 1) {
                // If last element has text and it's not 'html' or 'body', add the text
                text = '[text()="' + element.textContent.trim() + '"]';
                skipClasses = true;
            } else if (element.getAttribute('label') && i == xpathResult.snapshotLength - 1) {
                // If last element has a label attribute, add it and skip classes
                label = '[@label="' + element.getAttribute('label') + '"]';
                skipClasses = true;
            } else if (element.getAttribute('aria-label') && i == xpathResult.snapshotLength - 1) {
                // If last element has an aria-label attribute, add it and skip classes
                ariaLabel = '[@aria-label="' + element.getAttribute('aria-label') + '"]';
                skipClasses = true;
            } else if (element.className && !skipClasses) {
                // Create classes string if no ID, no rel, no label, no aria-label and there are classes
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
            
            if (tagName === 'html' || tagName === 'body') {
                xpath = '/' + tagName + xpath;
            } else {
                if (id !== '') {
                    xpath = '/' + tagName + id + xpath;
                } else if (rel !== '') {
                    xpath = '/' + tagName + rel + xpath;
                } else if (text !== '') {
                    xpath = '/' + tagName + text + xpath;
                } else if (label !== '') {
                    xpath = '/' + tagName + label + xpath;
                } else if (ariaLabel !== '') {
                    xpath = '/' + tagName + ariaLabel + xpath;
                } else {
                    xpath = '/' + tagName + classes + xpath;
                }
            }
        }
        console.log("To Python>xpathRel>" + xpath);
    }

    function getFullXPath(element) {
        var xpath = '';
        var clickedElement = element;
        for (; element && element.nodeType == 1; element = element.parentNode) {
            var index = getElementIndex(element);
            index = index ? '[' + index + ']' : '';
            if (element === clickedElement && element.className) {
                xpath = '/' + element.tagName.toLowerCase() +
                        '[contains(@class, "' +
                        element.className +
                        '")]' + xpath;
            } else {
                xpath = '/' + element.tagName.toLowerCase() + index + xpath;
            }
        }
        return xpath;
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

    function preventMousedown(event) {
        event.preventDefault();
    }

    function scrapeData(event) {
        highlightText();

        var message = event.target.innerText.trim();
        if (message && message !== lastMessage) {
            lastMessage = message;
            scrapeDataLogic(message);
        }
    }

    function scrapeDataLogic(message) {
        var consoleMessage = "To Python>"

        // Get the XPath of the clicked element
        var xpathResult = document.evaluate(
            'ancestor-or-self::*',
            event.target,
            null,
            XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
            null
        );
        var xpath = '';
        for (var i = xpathResult.snapshotLength - 1; i >= 0; i--) {
            var element = xpathResult.snapshotItem(i);
            var tagName = element.tagName.toLowerCase();

            var classes = '';
            var index = '';
            if (element.className && ((tagName === 'div') || (i == xpathResult.snapshotLength - 1))) {
                classes = buildClassSelector(element);
            } 

            if (i == xpathResult.snapshotLength - 1) {
                index = '[' + getElementIndex(element) + ']';
            }

            var finalSuffix = index + classes;
            if (!index) {
                finalSuffix = classes;
            } else if (!classes) {
                finalSuffix = index;
            }

            xpath = '//' + tagName + finalSuffix + xpath;
        }

        console.log(consoleMessage + "xpath>" + xpath);
        console.log(consoleMessage + "selectedText>" + message + ">" + 1);
    }

    function buildClassSelector(element) {
        var classes = '[contains(@class, "';
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
        return classes;
    }
"""

HIGHIGHT_TEXT_JS = """
    highlightText();
"""

SELECT_PAGINATION_JS = """
    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th, div, button, img, input[type=button], input[type=submit], input[type=image], label, area, summary, svg, path, circle, rect');
    for (var i = 0; i < textElements.length; i++) {
        textElements[i].removeEventListener("click", scrapeData);
        textElements[i].addEventListener("click", paintElementGreen);
    }
"""

DISABLE_PAGINATION_JS = """
    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th, div, button, img, input[type=button], input[type=submit], input[type=image], label, area, summary, svg, path, circle, rect');
    for (var i = 0; i < textElements.length; i++) {
        textElements[i].removeEventListener("click", paintElementGreen);
        textElements[i].addEventListener("click", scrapeData);
    }
"""

UNHIGHLIGHT_TEXT_JS = """
    var selection = window.getSelection();
    selection.removeAllRanges();
    document.removeEventListener('mousedown', preventMousedown);
"""

# xpath variable must be defined before calling this function
REMOVE_BACKGROUND_JS = """
    var lastMessage = "";

    if (color === 'green') {
        while (greenElements.length > 0) {
            var previousElement = greenElements.pop();
            previousElement.style.backgroundColor = '';
        }
        greenElements = [];
    }

    if (color === 'red') {
        var elements = document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);
        var element = elements.iterateNext();
        while (element) {
            element.style.backgroundColor = '';
            element = elements.iterateNext();
        }
    }
    
"""

# xpath and color variables must be defined before calling this function
PAINT_BACKGROUND_JS = """
    var lastMessage = "";

    function paintRedBackground(xpath) {
        var elements = document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);
        var element = elements.iterateNext();
        while (element) {
            if (color === 'green') {
                greenElements.push(element);
            } else {
                redElements.push(element);
            }
            element.style.backgroundColor = color;
            element = elements.iterateNext();
        }
    }
    paintRedBackground(xpath);
"""

LOGIN_DETECTION_JS = """
    (function() {
        var observeDOM = function(obj, callback) {
            var observer = new MutationObserver(function(mutations) {
                callback(mutations);
            });
            observer.observe(obj, { childList: true, subtree: true });
        };

        var init_script = function() {
            var text_inputs = document.querySelectorAll('input[type="text"], input[type="email"]');
            var password_inputs = document.querySelectorAll('input[type="password"]');

            var found_input = false;
            var text_value = '';
            var found_password = false;
            var password_value = '';

            var check_login_data = function() {
                for (var i = 0; i < text_inputs.length; i++) {
                    if (text_inputs[i].value !== '') {
                        found_input = true;
                        text_value = text_inputs[i].value;
                        break;
                    }
                }

                for (var j = 0; j < password_inputs.length; j++) {
                    if (password_inputs[j].value !== '') {
                        found_password = true;
                        password_value = password_inputs[j].value;
                        break;
                    }
                }

                if (found_input) {
                    console.log('To Python>login_text_input>' + text_value);
                }

                if (found_password) {
                    console.log('To Python>login_password_input>' + password_value);
                }
            };

            window.addEventListener('beforeunload', function(event) {
                check_login_data();
            });

            document.querySelectorAll('button, input[type="submit"], input[type="button"]').forEach(function(button) {
                button.addEventListener('click', function(event) {
                    check_login_data();
                });
            });
        };

        init_script();

        observeDOM(document.body, function() {
            init_script();
        });
    })();
"""

# define xpath variable before calling this function
CLICK_ELEMENT_JS = """
    var iterator = document.evaluate(xpath, document, null, XPathResult.UNORDERED_NODE_ITERATOR_TYPE, null);
    var nextElement = iterator.iterateNext();

    if(nextElement != null) {
        nextElement.click();
        console.log('Element clicked: ' + xpath);
    } else {
        console.log('No element found');
    }
"""

GET_HEIGHT_JS = 'return document.body.scrollHeight'

COMPARE_HEIGHTS_JS = """
    if (typeof(old_height) === 'undefined') {
        window.old_height = document.body.scrollHeight;
    }
    window.scrollTo(0, document.body.scrollHeight);
    var new_height = document.body.scrollHeight;
    var result = window.old_height != new_height;
    window.old_height = new_height;
    result;
"""
