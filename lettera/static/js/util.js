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
  var data_year, data_month, data_day;


  d3.selection.prototype.moveToFront = function() { 
    return this.each(function() { 
      this.parentNode.appendChild(this); 
    }); 
  }; 

  d3.selection.prototype.moveToBack = function() { 
    return this.each(function() { 
        var firstChild = this.parentNode.firstChild; 
        if (firstChild) { 
            this.parentNode.insertBefore(this, firstChild); 
        } 
    }); 
  };

  var shift = function(x, d, dx) { 
    var ddx = new Date(d.getTime() + dx); 
    var r = x(ddx) - x(d);
    return r;
  };

  var redraw = function (x, y, height, root, data) {
    var dom = x.domain();
    var min = dom[0];
    var max = dom[1];
    var filter_data = data.filter(function(d) { return min <= d.x && x.invert(shift (x, d.x, d.dx)) <= max; });

    root.selectAll(".bar").remove();	
    
    var bar = root.selectAll(".bar").data(filter_data);
    var bar_enter = bar.enter();

    bar.exit().remove();

    var g = bar_enter.append("g")
                     .attr("class", "bar")
                     .attr("transform", function(d) { return "translate(" + x(d.x) + "," + y(d.y) + ")"; });

    g.append("rect")
        .attr("x", 1).attr("width", function(d){ return d3.max([shift(x, d.x, d.dx) - 1, 1]); })
                     .attr("height", function(d) { return height - y(d.y); });
	
    g.append("text")
        .attr("dy", ".75em")
        .attr("y", -12)
        .attr("text-anchor", "middle")
        .text(function(d) { return d.y > 0 ? formatCount(d.y) : ""; }).attr("x", function(d){ return shift(x, d.x,d.dx) / 2; });

  }

  var draw_periods = function (x, y, height, root, data) { 
    var dom = x.domain();
    var min = dom[0];
    var max = dom[1];
    var filter_data = data.filter(function(d) { 
      var y = x.invert(shift (x, d.x, d.dx));
      return d.x <= max 
          && min <= y; 
    });

    root.selectAll(".period").remove();	
    
    var bar = root.selectAll(".period").data(filter_data);
    var bar_enter = bar.enter();

    bar.exit().remove();
    
    var width_function = function (d) { return d3.max([shift(x, d.x, d.dx) - 1, 1]); }
    
    var g = bar_enter.append("g")
                     .attr("class", "period")
                     .attr("transform", function(d) { return "translate(" + x(d.x) + "," + 0 + ")"; });

    g.append("rect")
        .attr("x", 1).attr("width", width_function)
                     .attr("opacity", 0.5)
                     .attr("height", function(d) { return height; });
	
    g.append("text")
        .attr("dy", ".75em")
        .attr("y", +10)
        .attr("text-anchor", "start")
        .text(function(d) { 
          return width_function(d) > 10 ? d.name : '';
         }).attr("x", function(d){ return shift(x, d.x, d.dx) / 2; }); 
  };

  /* _ : days, 2 : month, 3 : year */

  var margin = {top: 10, right: 10, bottom: 100, left: 40},
      width = 960 - margin.left - margin.right,
      height1 = 200,
      height2 = 150,
      height3 = 150,
      height = height1 + height2 + height3 + 3*margin.top + 3*margin.bottom;

  var formatCount = d3.format(",.0f");

  var x = d3.time.scale().range([0, width]),
      y = d3.scale.linear().range([height1, 0]),
      xAxis = d3.svg.axis().scale(x).orient("bottom");
  
  var x2 = d3.time.scale().range([0, width]),
      y2 = d3.scale.linear().range([height2, 0]),
      xAxis2 = d3.svg.axis().scale(x2).orient("bottom");
  
  var x3 = d3.time.scale().range([0, width]),
      y3 = d3.scale.linear().range([height3, 0]),
      xAxis3 = d3.svg.axis().scale(x3).orient("bottom");

  var svg = d3.select(selector).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height);

  var group_day = svg.append("g")
      .attr("class", "day")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var group_month = svg.append("g")
      .attr("class", "month")
      .attr("transform", "translate(" + margin.left + "," + (height1 + 2*margin.top + margin.bottom) + ")");

  var group_year = svg.append("g")
      .attr("class", "year")
      .attr("transform", "translate(" + margin.left + "," + (height1 + height2 + 3 * margin.top + 2*margin.bottom) + ")");

  var brush_month = d3.svg.brush()
      .x(x2)
      .on("brush", brushed).on("brushend", brushended);
  
  var brush_year = d3.svg.brush()
      .x(x3)
      .on("brush", brushed).on("brushend", brushended);

  var extend_domain = function (interval, domain) {
     var start = interval.offset(domain[0], -1);
     var end = interval.offset(domain[1], +1);
     return [start, end];
  }

  getData (function (values, periods) {
    
    x.domain(extend_domain(d3.time.day, d3.extent(values))).range([0,width]);
    x2.domain(extend_domain(d3.time.month, x.domain()));
    x3.domain(extend_domain(d3.time.year, x.domain()));
    
    var start = x.domain()[0];
    var end = x.domain()[1];

    bins_day = d3.time.day.range(start, end);
    bins_month = d3.time.month.range(start, end);
    bins_year = d3.time.year.range(start, end);
    
    data_periods = periods.map(function(d) {
       return { "x" : d.start, "dx" : (d.end.getTime() - d.start.getTime()), "name" : d.name };
    });

    data_day = d3.layout.histogram().bins(bins_day)(values);
    data_month = d3.layout.histogram().bins(bins_month)(values);
    data_year = d3.layout.histogram().bins(bins_year)(values);

    y.domain([0, d3.max(data_day, function(d) { return d.y; })]).range([height1, 0]);
    y2.domain([0, d3.max(data_month, function(d) { return d.y; })]).range([height2, 0]);
    y3.domain([0, d3.max(data_year, function(d) { return d.y; })]).range([height3, 0]);
    

    group_day.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height1 + ")")
        .call(xAxis);

    group_month.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height2 + ")")
        .call(xAxis2);
    
    draw_periods(x3, y3, height3, group_year, data_periods);
    redraw(x3, y3, height3, group_year, data_year);
    
    group_year.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height3 + ")")
        .call(xAxis3);
  
    random_value = values[Math.floor(Math.random() * values.length / 2)];
    random_value_year = d3.time.year.offset(random_value, 1);
    random_value_month1 = d3.time.month.offset(random_value, 1);
    random_value_month2 = d3.time.month.offset(random_value_month1, 1);

    brush_year.extent([random_value, random_value_year]);
    x2.domain(brush_year.extent());
    brush_month.extent([random_value_month1, random_value_month2]);

    group_month.append("g")
        .attr("class", "x brush")
        .call(brush_month)
        .selectAll("rect")
        .attr("y", -6)
        .attr("height", height2 + 7);

    group_year.append("g")
        .attr("class", "x brush")
        .call(brush_year)
        .selectAll("rect")
        .attr("y", -6)
        .attr("height", height3 + 7);

    brushed();
  });

  function brushended() {
   // updateHist();
  }

  function brushed() {
    x2.domain(brush_year.empty() ? x3.domain() : brush_year.extent());
    brush_month.x(x2);
    x.domain(brush_month.empty() ? x2.domain() : brush_month.extent());
    
    draw_periods(x2, y2, height3, group_month, data_periods);
    draw_periods(x, y, height1, group_day, data_periods);
    redraw(x, y, height1, group_day, data_day);
    redraw(x2, y2, height2, group_month, data_month);
    group_month.select(".x.brush").moveToFront();
    group_year.select(".x.brush").moveToFront();
    group_month.select(".x.axis").call(xAxis2).moveToFront();
    group_day.select(".x.axis").call(xAxis).moveToFront();
  }
}
