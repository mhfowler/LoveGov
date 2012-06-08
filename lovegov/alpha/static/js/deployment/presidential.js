var strokeColor;
var fillColor;
var hoverStrokeColor;
var hoverFillColor;

var imgRef;
var topicDirectory = "/static/images/questionIcons/";

var nodeName;

var hoverObj = {hoverShape:null,hoverText:null};

var numberOfTopics = 7;
var length = 300;
var skew = 105;
var radiusTopic = 30;
var radiusMiddle = 45;

function loadPresidentialComparisons()
{
    var comparisons = $('#result-json').text();
    var obj = jQuery.parseJSON(comparisons);
    for (var j=0; j<obj.length;j++)
    {
        var stage = new Kinetic.Stage(obj[j].candidate+"-canvas", length, length);
        var shapesLayer = new Kinetic.Layer();
        var imagesLayer = new Kinetic.Layer();
        var textLayer = new Kinetic.Layer();
        var hoverLayer = new Kinetic.Layer();
        var canvasDict = {'stage':stage,'shapesLayer':shapesLayer,'imagesLayer':imagesLayer,'textLayer':textLayer,'hoverLayer':hoverLayer};
        $.each(jQuery.parseJSON(obj[j].comparison), function(index, value)
        {
            drawTopicByJSON(value,canvasDict);
        });
        stage.add(shapesLayer);
        stage.add(imagesLayer);
        stage.add(textLayer);
        stage.add(hoverLayer);
    }
}


function drawTopicByJSON(topicObj,canvasDict)
{
    switch(topicObj[0])
    {
        case 'Economy':
            setColorDrawTopicImgs(0);
            drawComparisonCircleJSON(topicObj, radiusTopic, 0, canvasDict);
            break;
        case 'Education':
            setColorDrawTopicImgs(1);
            drawComparisonCircleJSON(topicObj, radiusTopic, 1, canvasDict);
            break;
        case 'Energy':
            setColorDrawTopicImgs(2);
            drawComparisonCircleJSON(topicObj, radiusTopic, 2, canvasDict);
            break;
        case 'Environment':
            setColorDrawTopicImgs(3);
            drawComparisonCircleJSON(topicObj, radiusTopic, 3, canvasDict);
            break;
        case 'Health Care':
            setColorDrawTopicImgs(4);
            drawComparisonCircleJSON(topicObj, radiusTopic, 4, canvasDict);
            break;
        case 'National Security':
            setColorDrawTopicImgs(5);
            drawComparisonCircleJSON(topicObj, radiusTopic, 5, canvasDict);
            break;
        case 'Social Issues':
            setColorDrawTopicImgs(6);
            drawComparisonCircleJSON(topicObj, radiusTopic, 6, canvasDict);
            break;
        case 'main':
            setColorDrawTopicImgs(7);
            drawMainCircle(length/2,length/2,radiusMiddle,topicObj[1]/100, topicObj[2],canvasDict);
            break;
        default:
            setColorDrawTopicImgs(7);
            break;
    }
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
            strokeColor = '#9DC5C9';
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
            imgRef = topicDirectory + "environment/env_mini.png";
            nodeName = 'environment';
            break;
        case 4:
            fillColor = '#E8B8C6';
            strokeColor = '#EA7D95';
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
            fillColor = '#ff8575';
            strokeColor = '#ef553f';
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



function drawMainCircle(x, y, radius, percentage, num_q,canvasDict)
{
    var circle = createCircle(x,y,radius,percentage);
    // add circle to layer
    canvasDict['shapesLayer'].add(circle);
    // bind mouseover function
    circle.on("mouseover", function()
    {
        if (this != canvasDict['shapesLayer'].getChildren()[canvasDict['shapesLayer'].getChildren().length-1])
        {
            circle.mouseOver();
        }
        canvasDict['shapesLayer'].draw();
    });
    // bind mouseout function
    circle.on('mouseout',function()
    {
        $("#match-hover").css({visibility:"hidden"});
        if (this != canvasDict['shapesLayer'].getChildren()[canvasDict['shapesLayer'].getChildren().length-1])
        {
            circle.mouseOut();
        }
        canvasDict['shapesLayer'].draw();
    });

    canvasDict['textLayer'].add(createText((percentage*100).toFixed() + '%',x,y,14));
    canvasDict['textLayer'].add(createText(num_q.toString(),x,y+radius+10,8));
}


function drawComparisonCircleJSON(topicObj, radius, order, canvasDict)
{
    // instance variables
    var x = (Math.cos(2 * Math.PI * (order/numberOfTopics)) * skew) + (length/2);
    var y = (Math.sin(2 * Math.PI * (order/numberOfTopics)) * skew) + (length/2);
    var num_q = topicObj[2];
    var percentage = topicObj[1]/100;

    // add new circle to shapesLayer
    var circle = createCircle(x,y,radius,percentage);
    canvasDict['shapesLayer'].add(circle);

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
            canvasDict['hoverLayer'].add(hoverObj.hoverShape);
            canvasDict['hoverLayer'].add(hoverObj.hoverText);
            canvasDict['hoverLayer'].draw();

            /*
             $("#match-hover").css({visibility:"visible",left:x-22,top:y-28});
             $("#match-hover").html('<img src="/static/catherine/home/hover-percent.png" style="z-index:-10"/>');
             $("#match-hover").append('<a style="z-index:10;position:absolute;top:17px;left:8px;color:#000000">' + Math.round(percentage*100) + "%" + '</a>');*/
            if (this != canvasDict['shapesLayer'].getChildren()[canvasDict['shapesLayer'].getChildren().length-1])
            {
                circle.mouseOver();
            }
            this.alpha = 1;
            canvasDict['shapesLayer'].draw();
            canvasDict['imagesLayer'].draw();
        });
        // bind mouseout function
        image.on('mouseout',function()
        {
            canvasDict['hoverLayer'].remove(hoverObj.hoverShape);
            canvasDict['hoverLayer'].remove(hoverObj.hoverText);
            canvasDict['hoverLayer'].draw();
            //$("#match-hover").css({visibility:"hidden"});
            if (this != canvasDict['shapesLayer'].getChildren()[canvasDict['shapesLayer'].getChildren().length-1])
            {
                circle.mouseOut();
            }
            this.alpha = 0.8;
            canvasDict['shapesLayer'].draw();
            canvasDict['imagesLayer'].draw();
        });
        canvasDict['imagesLayer'].add(image);
        canvasDict['imagesLayer'].draw();
    };
    imageObj.src = imgRef;
    canvasDict['textLayer'].add(createText(num_q.toString(),x,y+radius+10,8));
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
