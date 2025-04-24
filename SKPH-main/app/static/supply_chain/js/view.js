const VIEW = {
    AVALIABLE_RESOURCES: 'avaliable-resources',
    DONATED_ITEMS: 'donated-items',
    DONATED_MONEY: 'donated-money',
    PENDING_REQUESTS: 'pending-requests',
    REQUEST_HISTORY: 'request-history',
    AVALIABLE_MONEY: 'avaliable-money'
  }




let hideAllItems = function () {
    for (let value in VIEW) {
      console.log(VIEW[value])
      let currElement = document.getElementById(VIEW[value]);
      if (currElement) {
        currElement.style['display'] = 'none';
      }
    }
  }

  let changeView = function (view) {
    if(typeof(VIEW, view)) {
      hideAllItems();
      console.log(view)
      let currElement = document.getElementById(view);
      if(currElement) {
        currElement.style['display'] = 'block';
      }
    }
  }

  document.addEventListener('DOMContentLoaded', function() {
    hideAllItems()
    changeView(VIEW.AVALIABLE_RESOURCES)
 }, false);


