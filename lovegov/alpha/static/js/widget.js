/* lovegov widget */

/* script to be inserted:

 <script id="lovegov-widget" src="http://dev.lovegov.com/static/js/widget.js"></script>

 */
var lovegov = "http://dev.lovegov.com";

(function() {

    // Localize jQuery variable
    var jQuery;

    /******** Load jQuery if not present *********/
    if (window.jQuery === undefined || window.jQuery.fn.jquery !== '1.7.1') {
        var script_tag = document.createElement('script');
        script_tag.setAttribute("type","text/javascript");
        script_tag.setAttribute("src",
            "http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js");
        if (script_tag.readyState) {
            script_tag.onreadystatechange = function () { // For old versions of IE
                if (this.readyState == 'complete' || this.readyState == 'loaded') {
                    scriptLoadHandler();
                }
            };
        } else {
            script_tag.onload = scriptLoadHandler;
        }
        // Try to find the head, otherwise default to the documentElement
        (document.getElementsByTagName("head")[0] || document.documentElement).appendChild(script_tag);
    } else {
        // The jQuery version on the window is the one we want to use
        jQuery = window.jQuery;
        main();
    }

    /******** Called once jQuery has loaded ******/
    function scriptLoadHandler() {
        // Restore $ and window.jQuery to their previous values and store the
        // new jQuery in our local jQuery variable
        jQuery = window.jQuery.noConflict(true);
        // Call our main function
        main();
    }

    /******** Our main function ********/
    function main() {
        jQuery(document).ready(function($) {
            /******* Load CSS *******/
            var css_link = $("<link>", {
                rel: "stylesheet",
                type: "text/css",
                href: lovegov + "/static/css/widget.css"
            });
            css_link.appendTo('head');

            /******* Create Widget Div *******/
            $('#lovegov-widget').after('<div id="lovegov-widget-container"> test </div>');


            /******* Load HTML *******/
            var hostname = window.location.hostname;
            var path=window.location.pathname;
            var jsonp_url = lovegov + "/widget/access/?";
            jsonp_url += "which=questions";
            jsonp_url += "&host=" + hostname;
            jsonp_url += "&path=" + path;
            jsonp_url += "&callback=?";
            alert(jsonp_url);
            $.getJSON(jsonp_url, function(data) {
                $('#lovegov-widget-container').html(data.html);
            });
        });
    }

})(); // We call our anonymous function immediately