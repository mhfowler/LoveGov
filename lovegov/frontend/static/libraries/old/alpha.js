var stage;
var shapesLayer;
var strokeColor;
var fillColor;
var hoverStrokeColor;
var hoverFillColor;
var imgRef;
var topicDirectory = "/static/questionIcons/";
var imagesLayer;
var nodeName;
var qaweb;

var textLayer;
var hoverLayer;

var hoverObj = {hoverShape:null,hoverText:null};

var numberOfTopics = 7;
var length = 300;
var skew = 105;
var radiusTopic = 30;
var radiusMiddle = 45;

$(window).load(function()
{
    stage = new Kinetic.Stage("qaweb", length, length);
    shapesLayer = new Kinetic.Layer();
    imagesLayer = new Kinetic.Layer();
    textLayer = new Kinetic.Layer();
    hoverLayer = new Kinetic.Layer();
    var comps = $("#comparison-json").text();
    var obj = jQuery.parseJSON(comps);
    $.each(obj, function(index, value)
    {
        drawTopicByJSON(value);
    });
    stage.add(shapesLayer);
    stage.add(imagesLayer);
    stage.add(textLayer);
    stage.add(hoverLayer);

    ('#qaweb').bind("mouseout",canvasMouseOut);
});

function drawTopicByJSON(topicObj)
{
    switch(topicObj[0])
    {
        case 'Economy':
            setColorDrawTopicImgs(0);
            drawComparisonCircleJSON(topicObj, radiusTopic, 0);
            break;
        case 'Education':
            setColorDrawTopicImgs(1);
            drawComparisonCircleJSON(topicObj, radiusTopic, 1);
            break;
        case 'Energy':
            setColorDrawTopicImgs(2);
            drawComparisonCircleJSON(topicObj, radiusTopic, 2);
            break;
        case 'Environment':
            setColorDrawTopicImgs(3);
            drawComparisonCircleJSON(topicObj, radiusTopic, 3);
            break;
        case 'Health Care':
            setColorDrawTopicImgs(4);
            drawComparisonCircleJSON(topicObj, radiusTopic, 4);
            break;
        case 'National Security':
            setColorDrawTopicImgs(5);
            drawComparisonCircleJSON(topicObj, radiusTopic, 5);
            break;
        case 'Social Issues':
            setColorDrawTopicImgs(6);
            drawComparisonCircleJSON(topicObj, radiusTopic, 6);
            break;
        case 'main':
            setColorDrawTopicImgs(7);
            drawMainCircle(length/2,length/2,radiusMiddle,topicObj[1]/100, topicObj[2]);
            break;
        default:
            setColorDrawTopicImgs(7);
            break;
    }
}

function canvasMouseOut()
{
    for (var i=0; i<shapesLayer.getChildren().length-1; i++)
    {
        shapesLayer.getChildren()[i].mouseOut();
    }
    $("#match-hover").css({visibility:"hidden"});
    shapesLayer.draw();
}








/**
 * This function is a switch to select fill/stroke colors and to draw image icon for topic
 *
 * @param topicID   the ID of the topic
 */
function setColorDrawTopicImgs(topicID)
{
    switch(topicID)
    {
        case 0:
            fillColor = '#CBE0AF';
            strokeColor = '#92B76C';
            hoverFillColor = fillColor;
            hoverStrokeColor = strokeColor;
            imgRef = topicDirectory + "economy/eco_mini.png";
            nodeName = 'economy';
            break;
        case 1:
            fillColor = '#C3E7ED';
            strokeColor = '#90D5E0';
            hoverFillColor = fillColor;
            hoverStrokeColor = strokeColor;
            imgRef = topicDirectory + "education/edu_mini.png";
            nodeName = 'education';
            break;
        case 2:
            fillColor = '#FFF0C5';
            strokeColor = '#F9D180';
            hoverFillColor = fillColor;
            hoverStrokeColor = strokeColor;
            imgRef = topicDirectory + "energy/ene_mini.png";
            nodeName = 'energy';
            break;
        case 3:
            fillColor = '#CACAD8';
            strokeColor = '#9797C6';
            hoverFillColor = fillColor;
            hoverStrokeColor = strokeColor;
            imgRef = topicDirectory + "environment/ene_mini.png";
            nodeName = 'environment';
            break;
        case 4:
            fillColor = '#E8B8C6';
            strokeColor = '#639E9B';
            hoverFillColor = fillColor;
            hoverStrokeColor = strokeColor;
            imgRef = topicDirectory + "health care/hea_mini.png";
            nodeName = 'foreign';
            break;
        case 5:
            fillColor = '#F9BFB4';
            strokeColor = '#EA947D';
            hoverFillColor = fillColor;
            hoverStrokeColor = strokeColor;
            imgRef = topicDirectory + "national security/nat_mini.png";
            nodeName = 'reform';
            break;
        case 6:
            fillColor = '#A3C6C4';
            strokeColor = '#639E9B';
            hoverFillColor = fillColor;
            hoverStrokeColor = strokeColor;
            imgRef = topicDirectory + "social issues/soc_mini.png";
            nodeName = 'social issues';
            break;
        case 7:
            fillColor = '#f6432b';
            strokeColor = '#ff1f01';
            hoverFillColor = fillColor;
            hoverStrokeColor = strokeColor;
            imgRef = topicDirectory + "economy.png";
            nodeName = 'Main';
            break;
        default:
            fillColor = '#ffa590';
            strokeColor = '#fb866c';
            hoverFillColor = '#c7c2e2';
            hoverStrokeColor = '#de5e40';
            imgRef = null;
            nodeName = '';
            break;
    }
}



function drawMainCircle(x, y, radius, percentage, num_q)
{
    var circle = createCircle(x,y,radius,percentage);
    // add circle to layer
    shapesLayer.add(circle);
    // bind mouseover function
    circle.on("mouseover", function()
    {
        if (this != shapesLayer.getChildren()[shapesLayer.getChildren().length-1])
        {
            circle.mouseOver();
        }
        shapesLayer.draw();
    });
    // bind mouseout function
    circle.on('mouseout',function()
    {
        $("#match-hover").css({visibility:"hidden"});
        if (this != shapesLayer.getChildren()[shapesLayer.getChildren().length-1])
        {
            circle.mouseOut();
        }
        shapesLayer.draw();
    });

    textLayer.add(createText((percentage*100).toFixed() + '%',x,y,14));
    textLayer.add(createText(num_q.toString(),x,y+radius+10,8));
}


function drawComparisonCircleJSON(topicObj, radius, order)
{
    // instance variables
    var x = (Math.cos(2 * Math.PI * (order/numberOfTopics)) * skew) + (length/2);
    var y = (Math.sin(2 * Math.PI * (order/numberOfTopics)) * skew) + (length/2);
    var num_q = topicObj[2];
    var percentage = topicObj[1]/100;

    // add new circle to shapesLayer
    var circle = createCircle(x,y,radius,percentage);
    shapesLayer.add(circle);

    var imageObj = new Image();
    imageObj.onload = function()
    {
        var image = new Kinetic.Image
            ({
                x: x-17,
                y: y-16,
                alpha:0.8,
                image: imageObj,
                width: 35,
                height: 35,
                zIndex:10
            });

        // bind mouseover function
        image.on("mouseover", function()
        {
            hoverObj.hoverShape = createHover(x,y-15);
            hoverObj.hoverText = createText(Math.round(percentage*100) + "%", x,y-35,10);
            hoverLayer.add(hoverObj.hoverShape);
            hoverLayer.add(hoverObj.hoverText);
            hoverLayer.draw();

            if (this != shapesLayer.getChildren()[shapesLayer.getChildren().length-1])
            {
                circle.mouseOver();
            }
            this.alpha = 1;
            shapesLayer.draw();
            imagesLayer.draw();
        });
        // bind mouseout function
        image.on('mouseout',function()
        {
            hoverLayer.remove(hoverObj.hoverShape);
            hoverLayer.remove(hoverObj.hoverText);
            hoverLayer.draw();
            //$("#match-hover").css({visibility:"hidden"});
            if (this != shapesLayer.getChildren()[shapesLayer.getChildren().length-1])
            {
                circle.mouseOut();
            }
            this.alpha = 0.8;
            shapesLayer.draw();
            imagesLayer.draw();
        });
        imagesLayer.add(image);
        imagesLayer.draw();
    };
    imageObj.src = imgRef;
    textLayer.add(createText(num_q.toString(),x,y+radius+10,8));
}

function createCircle(x, y, radius, percentage)
{
    return new Kinetic.Shape
        ({
            state: 0,
            radius: radius,
            stroke: new Array(strokeColor, hoverStrokeColor),
            fill: new Array(fillColor, hoverFillColor),
            zIndex:10,
            drawFunc: function()
            {
                var ctx = this.getContext("2d");
                ctx.beginPath();
                var startAngle = Math.asin(1-(2*percentage));
                var endAngle = Math.PI - startAngle;
                ctx.arc(x,y,this.radius,startAngle,endAngle,false);
                ctx.closePath();
                ctx.fillStyle = this.fill[this.state];
                ctx.fill();

                ctx.beginPath();
                ctx.arc(x,y,this.radius,0,2*Math.PI,false);
                ctx.closePath();
                ctx.strokeStyle = this.stroke[this.state];
                ctx.stroke();
            },
            mouseOver:function()
            {
                this.state = 1;
                this.radius = this.radius + 5;
            },
            mouseOut:function()
            {
                this.radius = this.radius - 5;
                this.state = 0;
            }
        });
}

function createText(string,x,y,fontSize)
{
    return new Kinetic.Text
        ({
            text:string,
            fontSize:fontSize,
            fontFamily:"Verdana",
            textFill:"black",
            x:x,
            y:y,
            align:"center",
            verticalAlign:"middle"
        });
}

function createHover(x,y)
{
    return new Kinetic.Shape
        ({
            drawFunc: function()
            {
                var context = this.getContext();
                context.beginPath();
                context.moveTo(x, y);
                context.lineTo(x+5, y-10);
                context.lineTo(x+18, y-10);
                context.quadraticCurveTo(x+19, y-11, x+20,y-12);
                context.lineTo(x+20, y-30);
                context.quadraticCurveTo(x+19, y-31, x+18, y-32);
                context.lineTo(x-18, y-32);
                context.quadraticCurveTo(x-19, y-31, x-20, y-30);
                context.lineTo(x-20, y-12);
                context.quadraticCurveTo(x-19, y-11, x-18, y-10);
                context.lineTo(x-5, y-10);
                context.lineTo(x, y);
                context.closePath();
                this.fillStroke();
            },
            fill: "#FFFFFF",
            stroke: "#4d8695",
            strokeWidth: 1
     });
}
