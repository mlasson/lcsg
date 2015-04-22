var corpus_list = {
  list : [],
  table : {},
  selector : $( ),
  add : function (s) {
    this.selector = this.selector.add(s);
  },
  reload : function() {
    var that = this;
    $.ajax({
      url: "{% url 'ajax-subcorpus-list' %}",
      dataType: "json",
      success: function(json){
          that.list = [];
          that.table = {};
          var length = json.length;
          for (var k = 0;k < length;k ++) {
            that.list.push(json[k]);
            that.table[json[k].pk]= json[k];
          }
          that.draw ();
        }
      });
   },
  get : function(pk) {
    return this.table[pk];
  },
  draw : function () {
    this.selector.empty();
    var length = this.list.length;
    this.list.sort(function(a, b) {
      if (a.name < b.name) 
        return -1;
      else if (b.name < a.name) 
        return 1;
      else 
        return 0;
    });
    for (var k = 0;k < length;k ++){
      var subcorpus = this.list[k];
      var name = subcorpus.name;
      var pk = subcorpus.pk;
      this.selector.append(($("<option>").append(name)).attr("data-corpus", name).attr("value", pk));
    }
  },
};

