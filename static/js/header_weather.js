$(document).ready(function () {
  console.log("test");
  $.ajax({
    type: "GET",
    url: "http://spartacodingclub.shop/sparta_api/weather/seoul",
    data: {},
    success: function (response) {
      let weather_City = response["city"];
      let weather_Image = response["icon"];
      let weather_Num = response["temp"];

      let weather_Total = `
                <p><b>오늘의 날씨 : ${weather_City}</b>
                ${weather_Num}도
                <image src = "${weather_Image}"width=30 height=30</image>
                </p>
                `;

      $(".weather").append(weather_Total);
    },
  });
});
