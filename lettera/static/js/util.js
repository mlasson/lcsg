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
    if (occ.family != "IGNORED WORDS") {
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
