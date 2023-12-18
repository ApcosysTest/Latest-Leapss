
  /**
   * Sidebar toggle
   */
  if (select('.toggle-sidebar-btn')) {
    on('click', '.toggle-sidebar-btn', function(e) {
        console.log("hbbib")
      select('body').toggle('toggle-sidebar')
    })
  }
