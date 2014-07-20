function draw_tree (fw_json, bw_json, anchor) {
  var m = [20, 120, 20, 120],
      w = 600 - m[1] - m[3],
      h = 100 - m[0] - m[2],
      i = 0,
      fw_root, bw_root;

  var separation = 120;

  anchor = (typeof anchor === "undefined") ? "#tree" : anchor;

  var fw_tree = d3.layout.tree().size([h, w/2]);
  var bw_tree = d3.layout.tree().size([h, w/2]);

  var diagonal = d3.svg.diagonal()
      .projection(function(d) { return [d.y, d.x]; });

  var canvas = d3.select(anchor).append("svg:svg");
 
  var vis = canvas.attr("width", w + m[1] + m[3])
                  .attr("height", h + m[0] + m[2])
                  .append("svg:g")
                  .attr("transform", "translate(" + (w/2 + m[3]) + "," + m[0] + ")");
 
  var line = vis.append("line").attr("x1", 0).attr("x2", w/2).attr("y1",0).attr("y2",0).attr("stroke-width", 2).attr("color", "black")


  d3.json(fw_json, function (json) {
    fw_root = json;
    fw_root.x0 = h/2;
    fw_root.y0 = 0;

    function toggleAll(d) {
      if (d.children) {
        d.children.forEach(toggleAll);
        toggle(d);
      }
    }

  // Initialize the display to show a few nodes.
    fw_root.children.forEach(toggleAll);

    d3.json(bw_json, function (json) {
      bw_root = json;
      bw_root.x0 = h/2;
      bw_root.y0 = 0;

      // Initialize the display to show a few nodes.
      bw_root.children.forEach(toggleAll);
      update(fw_root);
      update(bw_root);
    });

  });

  function update(source) {
    var duration = d3.event && d3.event.altKey ? 5000 : 500;

    // compute the new height
    var levelWidth = [1];
    var childCount = function(level, n, k) {

      if(n.children && n.children.length > 0) {
        if(levelWidth.length <= 2*(level + 1)) {
          levelWidth.push(0);
          levelWidth.push(0);
        }
        levelWidth[2*level+k] += n.children.length;
        n.children.forEach(function(d) {
          childCount(level + 1, d, k);
        });
      }
    };
    childCount(0, fw_root, 0);  
    childCount(0, bw_root, 1);  
        // Compute the new tree layout.
    var fw_nodes = fw_tree.nodes(fw_root).reverse();
    var bw_nodes = bw_tree.nodes(bw_root).reverse();

    // Normalize for fixed-depth.
    fw_nodes.forEach(function(d) { 
        d.y = d.depth * separation; 
    });
    bw_nodes.forEach(function(d) { 
        d.y = -d.depth * separation; 
    });

    fw_root.x = h/2;
    bw_root.x = h/2;
    
    h = d3.max(levelWidth) * 20 + levelWidth.length * 5; // 20 pixels per line  
    var fw_depth = d3.max(fw_nodes, function(x) { return x.depth;});
    var bw_depth = d3.max(bw_nodes, function(x) { return x.depth;});

    fw_w =  fw_depth * separation;
    bw_w =  bw_depth * separation;
    w = fw_w + bw_w;
    fw_tree = fw_tree.size([h, fw_w]);
    bw_tree = bw_tree.size([h, bw_w]);
    canvas.attr('height', h + m[0]+m[2]);
    canvas.attr('width', w + m[1]+m[3]);
    vis.attr("transform", "translate(" + (bw_w + m[3]) + "," + m[0] + ")");

    

    // Update the nodes…
    nodes = fw_nodes.concat(bw_nodes);
    var node = vis.selectAll("g.node")
	.data(nodes, function(d) { return d.id || (d.id = ++i); });

    var update_node = function(node, nodes, tree) {
      // Enter any new nodes at the parent's previous position.
      var nodeEnter = node.enter().append("svg:g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
      .on("click", function(d) { toggle(d); update(d); });

      nodeEnter.append("svg:circle")
      .attr("r", 1e-6)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

      nodeEnter.append("svg:text")
      .attr("x", function(d) { return d.children || d._children ? -10 : 10; })
      .attr("dy", ".35em")
      .attr("text-anchor", function(d) { return d.children || d._children ? "end" : "start"; })
      .text(function(d) { return d.name; })
      .style("fill-opacity", 1e-6);

      // Transition nodes to their new position.
      var nodeUpdate = node.transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

      nodeUpdate.select("circle")
      .attr("r", 4.5)
      .style("fill", function(d) { return d._children ? "lightsteelblue" : "#fff"; });

      nodeUpdate.select("text")
      .style("fill-opacity", 1);

      // Transition exiting nodes to the parent's new position.
      var nodeExit = node.exit().transition()
      .duration(duration)
      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
      .remove();

      nodeExit.select("circle")
      .attr("r", 1e-6);

      nodeExit.select("text")
      .style("fill-opacity", 1e-6);

      // Update the links…
      var link = vis.selectAll("path.link")
      .data(tree.links(nodes), function(d) { return d.target.id; });

      // Enter any new links at the parent's previous position.
      link.enter().insert("svg:path", "g")
      .attr("class", "link")
      .attr("d", function(d) {
        var o = {x: source.x0, y: source.y0};
        return diagonal({source: o, target: o});
      })
        .transition()
      .duration(duration)
      .attr("d", diagonal);

      // Transition links to their new position.
      link.transition()
      .duration(duration)
      .attr("d", diagonal);

      // Transition exiting nodes to the parent's new position.
      link.exit().transition()
      .duration(duration)
      .attr("d", function(d) {
        var o = {x: source.x, y: source.y};
        return diagonal({source: o, target: o});
      })
      .remove();

      // Stash the old positions for transition.
      nodes.forEach(function(d) {
        d.x0 = d.x;
        d.y0 = d.y;
      });
    }

    update_node(node, nodes, fw_tree);
    update_node(node, nodes, bw_tree);
  }

  // Toggle children.
  function toggle(d) {
    if (d.children) {
      d._children = d.children;
      d.children = null;
    } else {
      d.children = d._children;
      d._children = null;
    }
  }

}
