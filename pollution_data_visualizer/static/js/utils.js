(function(global){
  function markerColor(aqi){
    if (aqi <= 50) return 'green';
    if (aqi <= 100) return 'yellow';
    return 'red';
  }
  if (typeof module !== 'undefined' && module.exports){
    module.exports.markerColor = markerColor;
  } else {
    global.markerColor = markerColor;
  }
})(typeof window !== 'undefined' ? window : global);
