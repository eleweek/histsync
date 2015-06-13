$( document ).ready(function() {
    var html_escape = function(str) {
        return $('<div/>').text(str).html();
    };

    var quot_escape = function(str) {
        return str.replace(/"/g, "&quot;");
    };

    var update_command = function(command_id, command_description, command_text, title, success_button_label, on_success_callback) {
        bootbox.dialog({
            title: title,
            message:
                    '<div class="row">  ' +
                        '<div class="col-md-12"> ' +
                            '<form class="form-horizontal"> ' +
                                '<div class="form-group"> ' +
                                    '<label class="col-md-4 control-label" for="pbf-description' + command_id + '">Description</label> ' +
                                    '<div class="col-md-4"> ' +
                                        '<input id="pbf-description-' + command_id + '" name="pbf-description-' + command_id + '" type="text" placeholder="Description(can be empty)" value="' + quot_escape(command_description) + '" class="form-control input-md"> ' +
                                    '</div>' + 
                                '</div>' + 
                                '<div class="form-group"> ' +
                                    '<label class="col-md-4 control-label" for="pbf-command-' + command_id + '">Command</label> ' +
                                    '<div class="col-md-4"> ' +
                                        '<input id="pbf-command-' + command_id + '" name="pbf-command-' + command_id + '" type="text" placeholder="Command" class="form-control input-md" value="' + quot_escape(command_text) + '"> ' +
                                    '</div>' +
                                '</div>' +
                            '</form>' + 
                        '</div>' +
                    '</div>',
            buttons: {
                cancel: {
                    label: "Cancel",
                    className: "btn-default"
                },
                success: {
                    label: success_button_label,
                    className: "btn-success",
                    callback: on_success_callback
                }
            }
        });
    };

    var get_command_description = function(command_id) {
        var command_description_elem = $('.command-description-' + command_id);
        return command_description_elem.length > 0 ? command_description = command_description_elem.html().trim() : "";
    };

    var get_command_text = function(command_id) {
         return $('.pre-command-' + command_id).html().substring(3);
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
        $(this).hide();
        var that = this;
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
        var command_description = get_command_description(command_id);
        var command_text = get_command_text(command_id);
        update_command(command_id, command_description, command_text, "Publish command", "Publish", function() {
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
        });
    });

    $(".btn-edit-command").click(function() {
        var command_id = $(this).data('command-id');
        var that = this;
        var command_description = get_command_description(command_id);
        var command_text = get_command_text(command_id);
        update_command(command_id, command_description, command_text, "Edit command", "Update", function() {
            var command_text = $('#pbf-command-' + command_id).val();
            var command_description = $('#pbf-description-' + command_id).val();
            $.post("/_edit_command/" + command_id,
                    {
                        description: command_description,
                        command: command_text
                    }
                  ).done(function(done){
                    $(".pre-command-" + command_id).html(" $ " + html_escape(command_text));
                    $(".command-description-" + command_id).html(html_escape(command_description));
                    $.notify("Succesfully updated the command!");
                  }).fail(function() {
                    $.notify("Failed to update the command!");
                  });
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
