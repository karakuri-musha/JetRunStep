$(function() {
  $(".open").on("click", function() {
    $(this).parent('td').nextAll('td').find('.versions').toggle();
    $(this).hide();
    $(this).next().show();
  });
  $(".close").on("click", function() {
    $(this).parent('td').nextAll('td').find('.versions').toggle();
    $(this).hide();
    $(this).prev().show();
  });
});

