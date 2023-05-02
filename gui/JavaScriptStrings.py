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

    var lastMessage = "";
    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th, div');
    for (var i = 0; i < textElements.length; i++) {
        textElements[i].addEventListener("click", scrapeData);
    }

    function scrapeData(event) {
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
            if (i == xpathResult.snapshotLength - 1) {
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
                var xpathRel = '//' + tagName + classes;
                console.log(consoleMessage + "xpathRel>" + xpathRel);
            }

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
                    xpath = '//' + tagName + classes + xpath;
                } else {
                    if (i == xpathResult.snapshotLength - 1) {
                        var index = getElementIndex(element);
                        xpath = '//' + tagName + '[' + index + ']' + xpath;
                    } else {
                        xpath = '//' + tagName + xpath;
                    }
                }
            }
        }
        console.log(consoleMessage + "xpath>" + xpath);
        console.log(consoleMessage + "selectedText>" + message + ">" + 1);

        var elements = document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);  // Find all elements that match the XPath
        var count = 0;
        var element = elements.iterateNext();
        while (element) {
            count++;
            if (count <= 1) {
                // console.log(consoleMessage + "selectedText>" + element.innerText.trim() + ">" + count);
            }
            element.style.backgroundColor = 'red';  // Paint the element with a red background color
            redElements.push(element);
            element = elements.iterateNext();
        }
        console.log(consoleMessage + "count>" + count);
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

START_JS = """
    function paintElementGreen(event) {
        // Remove the green background color from the previously clicked element(s)
        while (greenElements.length > 0) {
            var previousElement = greenElements.pop();
            previousElement.style.backgroundColor = '';
        }

        var clickedElement = event.target;
        clickedElement.style.backgroundColor = 'green';
        greenElements.push(clickedElement);
    }

    function preventMousedown(event) {
        event.preventDefault();
    }
"""

SELECT_PAGINATION_JS = """
    var greenElements = [];

    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th, div');
    for (var i = 0; i < textElements.length; i++) {
        textElements[i].addEventListener("click", paintElementGreen);
    }
"""

DISABLE_PAGINATION_JS = """
    var textElements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, li, a, td, th, div');
    for (var i = 0; i < textElements.length; i++) {
        textElements[i].removeEventListener("click", paintElementGreen);
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

    document.addEventListener('mousedown', preventMousedown);
"""

UNHIGHLIGHT_TEXT_JS = """
    var selection = window.getSelection();
    selection.removeAllRanges();
    document.removeEventListener('mousedown', preventMousedown);
"""

# xpath variable must be defined before calling this function
REMOVE_RED_BACKGROUND_JS = """
    var lastMessage = "";

    function removeRedBackground(xpath) {
        var elements = document.evaluate(xpath, document, null, XPathResult.ANY_TYPE, null);
        var element = elements.iterateNext();
        while (element) {
            element.style.backgroundColor = '';
            element = elements.iterateNext();
        }
    }
    removeRedBackground(xpath);
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

            var find_button_near_password_input = function(password_input) {
                var parent = password_input.parentElement;
                var button = parent.querySelector('button, input[type="submit"], input[type="button"]');
                if (button) {
                    return button;
                }

                var siblings = parent.parentElement.children;
                for (var i = 0; i < siblings.length; i++) {
                    button = siblings[i].querySelector('button, input[type="submit"], input[type="button"]');
                    if (button) {
                        return button;
                    }
                }

                for (var i = 0; i < siblings.length; i++) {
                    button = siblings[i].querySelectorAll('button, input[type="submit"], input[type="button"]')[0];
                    if (button) {
                        return button;
                    }
                }

                return null;
            };

            var getElementXPath = function(element) {
                var xpath = '';
                for (; element && element.nodeType == 1; element = element.parentNode) {
                    var id = Array.prototype.indexOf.call(element.parentNode.children, element) + 1;
                    id > 0 ? (id = '[' + id + ']') : (id = '');
                    xpath = '/' + element.tagName.toLowerCase() + id + xpath;
                }
                return xpath;
            };

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
                    var button = find_button_near_password_input(password_inputs[j]);
                    var button_xpath = '';
                    if (button) {
                        button_xpath = getElementXPath(button);
                    }
                    console.log('To Python>login_button_xpath>' + button_xpath)
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
