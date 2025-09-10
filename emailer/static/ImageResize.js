"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var lodash_1 = require("lodash");
var Quill = require("quill");
var DefaultOptions_1 = require("./DefaultOptions");
var DisplaySize_1 = require("./modules/DisplaySize");
var Resize_1 = require("./modules/Resize");
var Toolbar_1 = require("./modules/Toolbar");
var knownModules = { DisplaySize: DisplaySize_1.DisplaySize, Resize: Resize_1.Resize, Toolbar: Toolbar_1.Toolbar };
/**
 * Enables Image Resizing on image elements in a Quill.Editor
 *
 * @export
 * @class ImageResize
 */
var ImageResize = /** @class */ (function () {
    function ImageResize(quill, options) {
        this.instance = quill;
        // Merge default options, overwrite with any passed in options
        this._options = lodash_1.merge({}, DefaultOptions_1.DefaultOptions, options);
        this.listeners = {
            onRootClick: this.onRootClick(),
            onKeyUp: this.onKeyUp()
        };
        // Disable native image resize in firefox
        document.execCommand('enableObjectResizing', false, 'false');
        this.instance.root.addEventListener('click', this.listeners.onRootClick, false);
        this.instance.root.parentElement.style.position = this.instance.root.parentElement.style.position || 'relative';
        this.modules = [];
    }
    /**
     * Re-initialize all internal modules, to active them
     *
     * @private
     *
     * @memberof ImageResize
     */
    ImageResize.prototype.initModules = function () {
        var self = this;
        this.destroyModules();
        if (this._options.modules)
            this.modules = this._options.modules.map(function (mclass) {
                return new (knownModules[mclass] || mclass)(self);
            });
        this.modules.forEach(function (module) {
            module.onCreate();
        });
        this.onUpdate();
    };
    ImageResize.prototype.destroyModules = function () {
        this.modules.forEach(function (module) {
            module.onDestroy();
        });
        this.modules = [];
    };
    /**
     * Event Handler to run when an element is clicked inside the Quill editor
     * Checks if the selected element is an image, and creates an overlay of the selected element
     *
     * @private
     * @returns {(evt: Event) => void}
     *
     * @memberof ImageResize
     */
    ImageResize.prototype.onRootClick = function () {
        var self = this;
        return function (event) {
            if (event.target && event.target['tagName'] && event.target['tagName'].toUpperCase() === 'IMG') {
                if (self.currentSelectedImage === event.target)
                    return; // Focuse is already up and running
                else if (self.currentSelectedImage)
                    self.hideSelection();
                self.showSelection(event.target);
            }
            else if (self.currentSelectedImage)
                self.hideSelection();
        };
    };
    /**
     * Hide the active overlay of active image
     *
     * @private
     * @returns
     *
     * @memberof ImageResize
     */
    ImageResize.prototype.hideSelection = function () {
        if (!this.currentSelectedImage)
            return;
        this.instance.root.parentNode.removeChild(this.currentOverlay);
        this.currentOverlay = null;
        document.removeEventListener('keyup', this.listeners.onKeyUp);
        this.instance.root.removeEventListener('input', this.listeners.onKeyUp);
        this.userSelectValue = '';
        this.destroyModules();
        this.currentSelectedImage = null;
    };
    /**
     * SHow the overlay of the image clicked
     *
     * @private
     * @param {HTMLElement} element
     *
     * @memberof ImageResize
     */
    ImageResize.prototype.showSelection = function (element) {
        this.currentSelectedImage = element;
        if (this.currentOverlay)
            this.hideSelection();
        this.instance.setSelection(null);
        this.userSelectValue = 'none';
        document.addEventListener('keyup', this.listeners.onKeyUp, true);
        this.instance.root.addEventListener('input', this.listeners.onKeyUp, true);
        this.createOverlayElement();
        this.instance.root.parentNode.appendChild(this.currentOverlay);
        this.reposition();
        this.initModules();
    };
    ImageResize.prototype.createOverlayElement = function () {
        this.currentOverlay = document.createElement('div');
        lodash_1.assign(this.currentOverlay.style, this._options.overlayStyles);
        return this.currentOverlay;
    };
    /**
     * Repositions the overlay, to follow the bound of the selected image
     *
     * @private
     * @returns
     *
     * @memberof ImageResize
     */
    ImageResize.prototype.reposition = function () {
        if (!this.currentOverlay || !this.currentSelectedImage)
            return;
        var parent = this.instance.root.parentElement;
        var imgRect = this.currentSelectedImage.getBoundingClientRect();
        var containerRect = parent.getBoundingClientRect();
        var repositionData = {
            left: imgRect.left - containerRect.left - 1 + parent.scrollLeft + "px",
            top: imgRect.top - containerRect.top + parent.scrollTop + "px",
            width: imgRect.width + "px",
            height: imgRect.height + "px",
        };
        lodash_1.assign(this.currentOverlay.style, repositionData);
    };
    /**
     * Updates each internal module
     *
     * @memberof ImageResize
     */
    ImageResize.prototype.onUpdate = function () {
        this.reposition();
        this.modules.forEach(function (module) {
            module.onUpdate();
        });
    };
    Object.defineProperty(ImageResize.prototype, "userSelectValue", {
        set: function (value) {
            var self = this;
            ['userSelect', 'mozUserSelect', 'webkitUserSelect', 'msUserSelect'].forEach(function (key) {
                self.instance.root.style[key] = value;
                document.documentElement.style[key] = value;
            });
        },
        enumerable: true,
        configurable: true
    });
    /**
     * Key Handler, for removing an image when DELETE or BACKSPACE is pressed
     *
     * @private
     * @returns {(event: KeyboardEvent) => void}
     *
     * @memberof ImageResize
     */
    ImageResize.prototype.onKeyUp = function () {
        var self = this;
        var KEYCODE_BACKSPACE = 8;
        var KEYCODE_DELETE = 46;
        return function (event) {
            if (self.currentSelectedImage) {
                if (event.keyCode === KEYCODE_DELETE || event.keyCode === KEYCODE_BACKSPACE)
                    Quill.find(self.currentSelectedImage).deleteAt(0);
            }
        };
    };
    Object.defineProperty(ImageResize.prototype, "overlay", {
        get: function () {
            return this.currentOverlay;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ImageResize.prototype, "image", {
        get: function () {
            return this.currentSelectedImage;
        },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(ImageResize.prototype, "options", {
        get: function () {
            return this._options;
        },
        enumerable: true,
        configurable: true
    });
    return ImageResize;
}());
exports.ImageResize = ImageResize;
//# sourceMappingURL=ImageResize.js.map