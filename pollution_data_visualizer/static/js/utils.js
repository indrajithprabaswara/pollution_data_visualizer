(function(global){
  function markerColor(aqi){
    if(aqi == null) return 'gray';
    if (aqi <= 50) return 'green';
    if (aqi <= 100) return 'yellow';
    if (aqi <= 150) return 'orange';
    if (aqi <= 200) return 'red';
    if (aqi <= 300) return 'purple';
    return 'maroon';
  }
  if (typeof module !== 'undefined' && module.exports){
    module.exports.markerColor = markerColor;
  } else {
    global.markerColor = markerColor;
  }
})(typeof window !== 'undefined' ? window : global);
