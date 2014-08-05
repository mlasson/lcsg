function format_letters(text) {
  // this is quite ugly, I hope whoever read that code will forgive me
  text = text.replace(/(\[)/, "<p>{{DEADBEEF}{"); // replace first [1] with {{DEADBEEF}{1]
  text = text.replace(/(\[[^\]]*\])/g, "</p><p>$1"); // replace all [...] with </p><p>[...]
  text = text.replace(/{{DEADBEEF}{/, "["); // replace back {{{ to [
  text = text + '</p>'; // add final end of paragraph
  return text;
}

function add_spans_letters(text, occurrences) {
  var position = 0;
  var result = "";
  var occ_len = occurrences.length; 
  for (var i = 0; i < occ_len; i ++){
    var occ = occurrences[i];
    result+= text.substring(position, occ.start_position);
    if (occ.family != "UNKNOWN WORDS") {
      result+= '<span class="bg-info" data-toggle="tooltip" data-placement="right" title="'+occ.family+'">';
    } else {
      result+= '<span class="bg-warning">';
    }
    result+= text.substring(occ.start_position, occ.end_position);
    result+= '</span>';
    
    position = occ.end_position;
  }
  return result;
}

function draw_period(getData, selector) {
  var data, values, start, end;
  var shift = function(x, d, dx) { 
    var ddx = new Date(d.getTime() + dx); 
    var r = x(ddx) - x(d);
    return r;
  };

  var margin = {top: 10, right: 10, bottom: 100, left: 40},
      width = 960 - margin.left - margin.right,
      height = 500 - margin.top - margin.bottom,
      margin2 = {top: 430, right: 10, bottom: 20, left: 40},
      height2 = 500 - margin2.top - margin2.bottom;

  var formatCount = d3.format(",.0f");

  var x = d3.time.scale().range([0, width]),
      y = d3.scale.linear().range([height, 0]);

  var xAxis = d3.svg.axis().scale(x).orient("bottom"),
      yAxis = d3.svg.axis().scale(y).orient("left");

  var svg = d3.select(selector).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

  var focus = svg.append("g")
      .attr("class", "focus")
      .attr("width", width)
      .attr("height", height)
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
   

  var x2 = d3.time.scale().range([0, width]),
      y2 = d3.scale.linear().range([height2, 0]),
      xAxis2 = d3.svg.axis().scale(x2).orient("bottom");
  
  var brush = d3.svg.brush()
      .x(x2)
      .on("brush", brushed).on("brushend", brushended);

  var context = svg.append("g")
      .attr("class", "context")
      .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

  getData (function (input) {
    values = input;
    x.domain(d3.extent(values)).range([0,width]);
    x2.domain(x.domain());

    focus.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);
    
    start = x.domain()[0];
    end = x.domain()[1];
    bins_day = d3.time.day.range(start, end);
    data = d3.layout.histogram().bins(bins_day)(values);
    y.domain([0, d3.max(data, function(d) { return d.y; })]).range([height, 0]);
    var bar = focus.selectAll(".bar").data(data, function (d){ return d; });

    bar.enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", function(d){ return d3.max([shift(x, d.x, d.dx) - 1, 1]); })
        .attr("height", function(d) { return height - y(d.y); });

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", 6)
        .attr("x", function(d){ return shift(x, d.x, d.dx) / 2; })
        .attr("text-anchor", "middle")
        .text(function(d) { return formatCount(d.y); });

    bins_month = d3.time.month.range(start, end);
    data2 = d3.layout.histogram().bins(bins_month)(values);
    y2.domain([0, d3.max(data2, function(d) { return d.y; })])
      .range([height2, 0]);



    var bar = context.selectAll(".bar")
        .data(data2)
        .enter().append("g")
        .attr("class", "bar")
        .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y2(d.y) + ")"; });

    bar.append("rect")
        .attr("x", 1)
        .attr("width", function(d){ return d3.max([shift(x2, d.x, d.dx) - 1, 1]); })
        .attr("height", function(d) { return height2 - y2(d.y); });

    bar.append("text")
        .attr("dy", ".75em")
        .attr("y", - 12)
        .attr("x", function(d){ return shift(x2, d.x,d.dx) / 2; })
        .attr("text-anchor", "middle")
        .attr("class", "above")
        .text(function(d) { return formatCount(d.y); });

    context.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height2 + ")")
        .call(xAxis);

    context.append("g")
        .attr("class", "x brush")
        .call(brush)
        .selectAll("rect")
        .attr("y", -6)
        .attr("height", height2 + 7);
  });

  function brushended() {
   // updateHist();
  }

  function brushed() {
    x.domain(brush.empty() ? x2.domain() : brush.extent());
    
    var bar = focus.selectAll(".bar").data(data, function (d){ return d; });
    bar.attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });
    bar.selectAll("rect").attr("width", function(d){ return d3.max([shift(x, d.x, d.dx) - 1, 1]); })
                         .attr("height", function(d) { return height - y(d.y); });
    bar.selectAll("text").attr("x", function(d){ return shift(x, d.x,d.dx) / 2; })
                         .text(function(d) { return formatCount(d.y); });
    
    focus.select(".x.axis").call(xAxis);
  }
}
