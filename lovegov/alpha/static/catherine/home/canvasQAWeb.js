var stage;
var shapesLayer;
var strokeColor;
var fillColor;
var hoverStrokeColor;
var hoverFillColor;
var imgRef;
var topicDirectory = "/static/catherine/home/topicIcons/";
var imagesLayer;
var nodeName;

$(document).ready(function()
{
    var length = 280;
    stage = new Kinetic.Stage("qaweb", length, length);
    shapesLayer = new Kinetic.Layer();
    imagesLayer = new Kinetic.Layer();
    var n = 7;
    var skew = 105;
    for (var i=0;i<7;i++)
    {
        var xpos = (Math.cos(2 * Math.PI * (i/n)) * skew) + (length/2);
        var ypos = (Math.sin(2 * Math.PI * (i/n)) * skew) + (length/2);
        setColorDrawTopicImgs(i);
        drawComparisonCircle(xpos,ypos,30,i*(1/7)+(1/7));
    }
    setColorDrawTopicImgs(null);
    drawComparisonCircle(length/2,length/2,45,1/2);
    stage.add(shapesLayer);
    stage.add(imagesLayer);
    $('#qaweb').bind("mouseout",canvasMouseOut);
});


function canvasMouseOut()
{
    for (var i=0; i<shapesLayer.getChildren().length-1; i++)
    {
        shapesLayer.getChildren()[i].mouseOut();
    }
    $('#match-hover').css({visibility:"hidden"});
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
            fillColor = '#bbd6ff';
            strokeColor = '#8dbaff';
            hoverFillColor = '#8dbaff';
            hoverStrokeColor = '#5f98ed';
            imgRef = topicDirectory + "economy.png";
            nodeName = 'economy';
            break;
        case 1:
            fillColor = '#afd48e';
            strokeColor = '#7ab742';
            hoverFillColor = '#7ab742';
            hoverStrokeColor = '#5e9d26';
            imgRef = topicDirectory + "education.png";
            nodeName = 'education';
            break;
        case 2:
            fillColor = '#e78fc1';
            strokeColor = '#d74497';
            hoverFillColor = '#d74497';
            hoverStrokeColor = '#b73c81';
            imgRef = topicDirectory + "energy.png";
            nodeName = 'energy';
            break;
        case 3:
            fillColor = '#97b3c2';
            strokeColor = '#528099';
            hoverFillColor = '#528099';
            hoverStrokeColor = '#40677b';
            imgRef = topicDirectory + "environment.png";
            nodeName = 'environment';
            break;
        case 4:
            fillColor = '#fcd58b';
            strokeColor = '#fbb414';
            hoverFillColor = '#fbb414';
            hoverStrokeColor = '#e5a419';
            imgRef = topicDirectory + "foreign.png";
            nodeName = 'foreign';
            break;
        case 5:
            fillColor = '#c7c2e2';
            strokeColor = '#a199ce';
            hoverFillColor = '#a199ce';
            hoverStrokeColor = '#7f78a6';
            imgRef = topicDirectory + "reform.png";
            nodeName = 'reform';
            break;
        case 6:
            fillColor = '#ffa590';
            strokeColor = '#fb866c';
            hoverFillColor = '#fb866c';
            hoverStrokeColor = '#de5e40';
            imgRef = topicDirectory + "social.png";

            break;
        default:
            fillColor = '#ffa590';
            strokeColor = '#fb866c';
            hoverFillColor = '#fb866c';
            hoverStrokeColor = '#de5e40';
            imgRef = null;
            nodeName = '';
            break;
    }
}


/**
 * This function draws a circle at (x,y) coordinate, radius, and percent fill
 *
 * @param x             the x coordinate to draw circle
 * @param y             the y coordinate to draw circle
 * @param radius        the radius of the circle
 * @param percentage    the percent of the circle to fill in
 */
function drawComparisonCircle(x, y, radius, percentage)
{
    var circle = createCircle(x,y,radius,percentage);
    // add circle to layer
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
            $('#match-hover').css({visibility:"visible",left:x-22,top:y-21});
            $('#match-hover').html('<img src="/static/catherine/home/hover-percent.png" style="z-index:-10"/>');
            $('#match-hover').append('<a style="z-index:10;position:absolute;top:17px;left:8px;color:#000000">' + Math.round(percentage*100) + "%" + '</a>');
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
            $('#match-hover').css({visibility:"hidden"});
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
                this.radius = 35;
            },
            mouseOut:function()
            {
                this.radius = 30;
                this.state = 0;
            }
        });
}