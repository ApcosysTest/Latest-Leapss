// Sidebar Toggle 
window.addEventListener('DOMContentLoaded', event => {

  // Toggle the side navigation
  const sidebarToggle = document.body.querySelector('#sidebarToggle');
  const sidebarClose = document.body.querySelector('#sidebarClose');
  if (sidebarToggle) {
    //   if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
    //       document.body.classList.toggle('sb-sidenav-toggled');
    //   }
      sidebarToggle.addEventListener('click', event => {
          event.preventDefault();
          document.body.classList.toggle('sb-sidenav-toggled');
        //   localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
      });
      sidebarClose.addEventListener('click', event => {
          event.preventDefault();
          document.body.classList.toggle('sb-sidenav-toggled');
        //   localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
      });
  }

});
function disdel(){
  $('.deleteEve').css('display','none')
  $('.dead').css('display','none') 
  $('.ded').css('display','block')  
  $('.ded').css('cursor','pointer')  
  $('.img2').css('display','block');
  $('.img1').css('display','none'); 
}
function candel(){
  $('.deleteEve').css('display','none')
  $('.dead').css('display','block') 
  $('.ded').css('display','none')  
  $('.img2').css('display','none');
  $('.img1').css('display','block'); 
}
$('textarea').keyup(function() {
    
  var characterCount = $(this).val().length,
      current = $('#current'),
      maximum = $('#maximum'),
      theCount = $('#the-count');
    
  current.text(characterCount);
  
  if (characterCount >= 30) {
    maximum.css('color', '#52D89C');
    current.css('color', '#52D89C');  
  } else {
    maximum.css('color','#FF7B5D'); 
  }
  
      
});
