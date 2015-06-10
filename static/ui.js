$( document ).ready(function() {
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
        $.post("/_publish_command/" + command_id).done(function(done){
            bootbox.confirm("Are you sure to publish the command?", function(result) {
                if (result) {
                    $(that).hide();
                    $(".btn-unpublish-command-" + command_id).show();
                    $(".public-title-" + command_id).show();
                    $(".private-title-" + command_id).hide();
                    $.notify("Succesfully published the command!");
                }
            });
        }).fail(function() {
            $(that).show();
            $.notify("Failed to publish the command!");
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
