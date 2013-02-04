; // defensive programming

var portl = function portl($) {
    var templates = {};

    $('script[type="text/x-handlebars-template"]').each(
        function(i, element) {
            var element = $(element);
            var template = Handlebars.compile(element.html());
            templates[element.attr('id')] = template;
        });

    function update_network(data) {
        $("#network-panel").html(templates["network"](data));
    }

    return {
        update_network: update_network
    }
}(jQuery);
