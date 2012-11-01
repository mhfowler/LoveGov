var stateAbbrArray = {'AK' : 'Alaska', 'AL' : 'Alabama', 'AR' : 'Arkansas', 'AZ' : 'Arizona', 'CA' : 'California',
    'CO' : 'Colorado', 'CT' : 'Connecticut', 'DE' : 'Delaware', 'DC' : 'District of Columbia', 'FL' : 'Florida',
    'GA' : 'Georgia', 'HI' : 'Hawaii', 'IA' : 'Iowa', 'ID' : 'Idaho', 'IL' : 'Illinois', 'IN' : 'Indiana',
    'KS' : 'Kansas', 'KY' : 'Kentucky', 'LA' : 'Louisiana', 'MA' : 'Massachusetts', 'MD' : 'Maryland',
    'ME' : 'Maine', 'MI' : 'Michigan', 'MN' : 'Minnesota', 'MS' : 'Mississippi', 'MO' : 'Missouri', 'MT' : 'Montana',
    'NC' : 'North Carolina', 'ND' : 'North Dakota', 'NE' : 'Nebraska', 'NH' : 'New Hampshire', 'NJ' : 'New Jersey',
    'NM' : 'New Mexico', 'NV' : 'Nevada', 'NY' : 'New York', 'OH' : 'Ohio', 'OK' : 'Oklahoma', 'OR' : 'Oregon',
    'PA' : 'Pennsylvania', 'RI' : 'Rhode Island', 'SC' : 'South Carolina', 'SD' : 'South Dakota',
    'TN' : 'Tennessee', 'TX' : 'Texas', 'UT' : 'Utah', 'VA' : 'Virginia', 'VT' : 'Vermont', 'WA' : 'Washington',
    'WI' : 'Wisconsin', 'WV' : 'West Virginia', 'WY' : 'Wyoming'};

var svgobj = document.getElementById('usmapsvg');
var FIRST_STATE_SELECTED = false;

svgobj.addEventListener("load", function() {
    var svgDoc = svgobj.contentDocument; //get the inner DOM
    var paths = svgDoc.getElementsByTagName('path'); //get the inner element by id
    for (var i=0; i<paths.length; i++) {
        var path = paths[i];
        path.addEventListener("click", function(e) {
            var target = e.target;
            if(target.className.baseVal=='selected') {
                target.className.baseVal = '';
                $('input.state_input').val('');
            } else {
                // unselect all states
                for(var j=0; j<paths.length; j++) {
                    var state = paths[j];
                    state.className.baseVal = '';
                }
                target.className.baseVal = 'selected';
                $('input.state_input').val(target.id);
            }
            if(!FIRST_STATE_SELECTED) {
                $('.find_address_button').tooltip('show');
                FIRST_STATE_SELECTED = true;
            }
        });
        path.addEventListener("mouseover", function(e) {
            var target = e.target;
           $('div.us_state_label').text(stateAbbrArray[target.id]).show();
        });
        path.addEventListener("mouseout", function(e) {
            var target = e.target;
            $('div.us_state_label').text('').hide();
        });


    }

    svgDoc.addEventListener('mousemove', function(e) {
        $('div.us_state_label').css({
            left:e.pageX,
            top:e.pageY + 170
        });
    });
});