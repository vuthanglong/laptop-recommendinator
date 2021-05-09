$(document).ready(function(){
    var mode = true;
    $("#adjust_icon").click(function(){
        if(mode == true)
        {
            document.documentElement.setAttribute('data-theme','dark');
            mode = false;
        }
        else
        {
            document.documentElement.setAttribute('data-theme', 'light');
            mode = true;
        }
    });
});