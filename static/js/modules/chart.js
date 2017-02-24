!(function(window ,$) {
    "use strict";

    var apiRoot = '/en/api/v1',
        chartDataRaw,
        tickerHistoryUrl = apiRoot +'/price/history',
        tickerLatestUrl = apiRoot + '/price/latest';

    function responseToChart(data) {
        var i,
            resRub = [],
            resUsd = [],
            resEur = [];

        for (i = 0; i < data.length; i+=2) {
            var sell = data[i],
            buy = data[i + 1];
            if(!!sell && !!buy) {
                resRub.push([Date.parse(sell.created_on), buy.price_rub_formatted, sell.price_rub_formatted]);
                resUsd.push([Date.parse(sell.created_on), buy.price_usd_formatted, sell.price_usd_formatted]);
                resEur.push([Date.parse(sell.created_on), buy.price_eur_formatted, sell.price_eur_formatted]);
            }
        }
        return {
            rub: resRub,
            usd: resUsd,
            eur: resEur
        };
    }

    function renderChart (currency, hours) {
        var actualUrl = tickerHistoryUrl;
        if (hours) {
            actualUrl = actualUrl + '?hours=' + hours;
        }
         $.get(actualUrl, function(resdata) {
            chartDataRaw = resdata;
            var data = responseToChart(resdata)[currency];
          $('#container-graph').highcharts({

                chart: {
                    type: 'arearange',
                    zoomType: 'x',
                    style: {
                        fontFamily: 'Gotham'
                    },
                    backgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
                        stops: [
                            [0, '#F3F3F3'],
                            [1, '#F3F3F3']
                        ]
                    },
                    events : {
                        load : function () {
                            // set up the updating of the chart each second
                            $('.highcharts-credits').remove();
                            var series = this.series[0];
                            setInterval(function () {
                                $.get(tickerLatestUrl, function (resdata) {
                                    var lastdata = responseToChart(resdata)[currency];
                                    if ( chartDataRaw.length && parseInt(resdata[0].unix_time) >
                                         parseInt(chartDataRaw[chartDataRaw.length - 1].unix_time)
                                    ) {
                                        //Only update if a ticker 'tick' had occured
                                        var _lastadata = lastdata[0];
                                        if (_lastadata[1] > _lastadata[2])
                                        {
                                            var a= _lastadata[1];
                                            _lastadata[1] = _lastadata[2];
                                            _lastadata[2] = a;
                                        }
                                        series.addPoint(_lastadata, true, true);
                                        Array.prototype.push.apply(chartDataRaw, resdata);
                                    }
                                });
                        }, 1000 * 30);
                      }
                    }
                },

                title: {
                    text: 'BTC/' + currency.toUpperCase()
                },

                xAxis: {
                    type: 'datetime',
                    dateTimeLabelFormats: {
                       day: '%e %b',
                        hour: '%H %M'

                    }
                },
                yAxis: {
                    title: {
                        text: null
                    }
                },

                tooltip: {
                    crosshairs: true,
                    shared: true,
                    valueSuffix: ' ' + currency.toLocaleUpperCase()
                },

                legend: {
                    enabled: false
                },

                series: [{
                    name: currency.toLowerCase() === 'rub' ? 'цена' : 'Price',
                    data: data,
                    color: '#8cc63f',
                    // TODO: fix this! make dynamic
                    pointInterval: 3600 * 1000
                }]
            });
        });
    }

    module.exports = {
        responseToChart:responseToChart,
        renderChart: renderChart,
        apiRoot: apiRoot,
        chartDataRaw: chartDataRaw,
        tickerHistoryUrl: tickerHistoryUrl,
        tickerLatestUrl: tickerLatestUrl
    };
}(window, window.jQuery)); //jshint ignore:line
