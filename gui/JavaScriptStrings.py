ENABLE_LINKS_JS = """
        var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
        links[i].removeEventListener("click", disableLink);
    }
"""

DISABLE_LINKS_JS = """
    var links = document.getElementsByTagName("a");
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener("click", disableLink);
    }

    function disableLink(event) {
        event.preventDefault();
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
