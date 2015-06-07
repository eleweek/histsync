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
            $('#api-key-value').html(data.api_key)
        });
    });
    $(".btn-delete").click(function() {
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
        $.post("/_star_command/" + command_id); // TODO: handling success/failure
    });
    $(".command-compact").click(function() {
        var command_id = $(this).data('command-id');
        $(".command-controls-" + command_id).toggle();
    });
});
