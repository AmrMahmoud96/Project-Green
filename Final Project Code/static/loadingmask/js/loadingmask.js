

function animateText() {
  console.log("Working");
  setInterval(function () {
      $('.loadingMaskText').fadeOut(750).delay(300).fadeIn(750).delay(300);
  }, 1400);
}
