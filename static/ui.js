$( document ).ready(function() {
    var html_escape = function(str) {
        return $('<div/>').text(str).html();
    };

    $.notifyDefaults({
        animate: {
            enter: 'animated fadeInDown',
            exit: 'animated fadeOutUp'
        }
    });
    $("#show-api-key").click(function() {
        $("#show-api-key").hide();
        $("#hide-api-key").show();
        $("#api-key").show();
    });
    $("#hide-api-key").click(function() {
        $("#show-api-key").show();
        $("#hide-api-key").hide();
        $("#api-key").hide();
    });
    $("#regenerate-api-key").click(function() {
        $.ajax("/_regenerate_api_key").done(function(data){
            $('#api-key-value').html(data.api_key);
        });
    });
    $(".btn-delete-command").click(function() {
        var command_id = $(this).data('command-id');
        var that = this;
        $(that).hide();
        $.post("/_delete_command/" + command_id).done(function(done){
            $("#command-row-" + command_id).remove();
            $.notify("Succesfully removed the command!");
        }).fail(function() {
            $(that).show();
            $.notify("Failed to remove the command!");
        });
    });
    $(".btn-star-command").click(function() {
        var command_id = $(this).data('command-id');
        var that = this;
        $.post("/_star_command/" + command_id).done(function(done){
            $(that).hide();
            $(".btn-unstar-command-" + command_id).show();
            $.notify("Succesfully starred the command!");
        }).fail(function() {
            $(that).show();
            $.notify("Failed to star the command!");
        });
    });
    $(".btn-publish-command").click(function() {
        var command_id = $(this).data('command-id');
        var that = this;
        bootbox.dialog({
            title: "Publishing command",
            message:
                    '<div class="row">  ' +
                        '<div class="col-md-12"> ' +
                            '<form class="form-horizontal"> ' +
                                '<div class="form-group"> ' +
                                    '<label class="col-md-4 control-label" for="pbf-description' + command_id + '">Description</label> ' +
                                    '<div class="col-md-4"> ' +
                                        '<input id="pbf-description-' + command_id + '" name="pbf-description-' + command_id + '" type="text" placeholder="Description(can be empty)" value="' + $('.command-description-' + command_id).html().trim() + '" class="form-control input-md"> ' +
                                    '</div>' + 
                                '</div>' + 
                                '<div class="form-group"> ' +
                                    '<label class="col-md-4 control-label" for="pbf-command-' + command_id + '">Command</label> ' +
                                    '<div class="col-md-4"> ' +
                                        '<input id="pbf-command-' + command_id + '" name="pbf-command-' + command_id + '" type="text" placeholder="Command" class="form-control input-md" value="' + $(that).data('command-text') + '"> ' +
                                    '</div>' +
                                '</div>' +
                            '</form>' + 
                        '</div>' +
                    '</div>',
            buttons: {
                success: {
                    label: "Publish",
                    className: "btn-success",
                    callback: function() {
                        var command_text = $('#pbf-command-' + command_id).val();
                        var command_description = $('#pbf-description-' + command_id).val();
                        $.post("/_publish_command/" + command_id,
                                {
                                    description: command_description,
                                    command: command_text
                                }
                              ).done(function(done){
                            $(that).hide();
                            $(".btn-unpublish-command-" + command_id).show();
                            $(".public-title-" + command_id).show();
                            $(".private-title-" + command_id).hide();
                            $(".pre-command-" + command_id).html(" $ " + html_escape(command_text));
                            $(".command-description-" + command_id).html(html_escape(command_description));
                            $.notify("Succesfully published the command!");
                        }).fail(function() {
                            $(that).show();
                            $.notify("Failed to publish the command!");
                        });
                    }
                }
            }
        });
    });

    $(".btn-unpublish-command").click(function() {
        var command_id = $(this).data('command-id');
        var that = this;
        bootbox.confirm("Are you sure to unpublish the command?", function(result) {
            if (result) {
                $.post("/_unpublish_command/" + command_id).done(function(done){
                    $(that).hide();
                    $(".btn-publish-command-" + command_id).show();
                    $(".public-title-" + command_id).hide();
                    $(".private-title-" + command_id).show();
                    $.notify("Succesfully made the command private!");
                }).fail(function() {
                    $(that).show();
                    $.notify("Failed make the command private!");
                });
            }
        });
    });

    $(".command-compact").click(function() {
        var command_id = $(this).data('command-id');
        $(".command-controls-" + command_id).toggle();
        var row = $(".command-row-" + command_id);
        if (row.hasClass('command-row-clicked')) {
            row.removeClass('command-row-clicked');
            row.find('pre').removeClass('code-compact-clicked');
        } else {
            row.addClass('command-row-clicked');
            row.find('pre').addClass('code-compact-clicked');
        }
    });
});
