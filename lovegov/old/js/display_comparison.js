/***********************************************************************************************************************
 * .js for displaying comparison
 *
 ***********************************************************************************************************************/

// global variables
var comparison_id;

/**
 *   Document Preparation
 */
$(document).ready(function(){
    comparison_id = $("#comparison_variables").children("#comparison_id").val();
});

/**
 * update comparison
 */
$("#updateCompare").click(function(){
    $.post('/action/', {'action':'updateCompare','c_id':comparison_id},
            // call back function
            function(data) {
                location.reload();
            });
});