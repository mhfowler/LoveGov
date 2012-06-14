/**
 * @author Clay
 *
 * This object handles generating visual comparisons on LoveGov. This object is extremely easy to use. Just call:
 *
 * new VisualComparison(divID,comparisonJSON).draw()
 *
 * Or, to be as explicit as possible, you may also reference the variable first before calling the draw method as such:
 *
 * var visualComparison = new VisualComparison(divID,comparisonJSON)
 * visualComparison.draw()
 *
 * @param divID:            the ID of the div to house the KineticJS Stage, no # included
 * @param comparisonJSON:   the comparison data from the server.  This object is somewhat complicated so I will note its
 *                          structure here.  Check models.py, class ViewComparison, def toJSON() for backend data generation.
 *                          {'main':{'result':<number>,'num_q':<number>},
 *                          'topics':['text':<string>,'colors':{'default':<string>,'light'<string>},'mini_img':<string>,
 *                                    'order':<number>,'result':<number>,'num_q':<number>]}
 */
var VisualComparison = Class.extend
({
    init: function(divID, comparisonJSON)
    {
        this.divID = divID;
        this.stage = null;
        this.hoverShape = null;
        this.hoverText = null;
        this.shapesLayer = new Kinetic.Layer();
        this.imagesLayer = new Kinetic.Layer();
        this.textLayer = new Kinetic.Layer();
        this.hoverLayer = new Kinetic.Layer();
        this.dataObj = comparisonJSON;
        this.numberOfTopics = this.dataObj['topics'].length;
        this.height = 300;
        this.width = 300;
        this.radiusTopic = 30;
        this.radiusMiddle = 45;
        this.skew = 100;
    },

    /**
     * The main drawing method.  This method draws the comparison
     */
    draw: function()
    {
        var self = this;
        $('#' + this.divID).css({height:self.height,width:self.width});
        this.stage = new Kinetic.Stage(self.divID,self.width,self.height);
        this.drawTopics();
        this.drawMiddle();
        this.addLayers();
    },

    /**
     * Draws the middle circle for the overall comparison
     */
    drawMiddle: function()
    {
        var self = this;
        var x = self.width/2; var y = self.width/2;
        var colorObject = {light:'#ff8575', default:'#ef553f'};
        var percentage = self.dataObj['main']['result']/100;
        var num_q = self.dataObj['main']['num_q'];
        var circle = createCircle(x,y,colorObject,self.radiusMiddle,percentage);
        var textobj = createText(num_q.toString() + " Q",x,y+25,8);
        circle.on("mouseover",function()
        {
            self.textLayer.add(textobj);
            self.textLayer.draw();
        });
        circle.on('mouseout',function()
        {
            self.textLayer.remove(textobj);
            self.textLayer.draw();
        });
        circle.on('click',function()
        {
            if (self.dataObj['user_url'] != '')
            {
                //ajaxLink(self.dataObj['user_url'],true);
            }
        });
        self.shapesLayer.add(circle);

        var percentText = createText((percentage*100).toFixed() + '%',x,y+8,16);
        percentText.on("mouseover",function()
        {
            self.textLayer.add(textobj);
            self.textLayer.draw();
        });
        percentText.on('mouseout',function(){
            self.textLayer.remove(textobj);
            self.textLayer.draw();
        });
        self.textLayer.add(percentText);


        //
    },

    /**
     * Iterates over the topic list and draws the comparison for each topic.
     */
    drawTopics: function()
    {
        var self = this;
        $.each(self.dataObj['topics'], function(index, topicObj)
        {
            var order = topicObj['order'];
            var result = topicObj['result'];
            var num_q = topicObj['num_q'];
            var percentage = topicObj['result']/100;
            var colorObject = topicObj['colors'];
            var imgRef = topicObj['mini_img'];
            var x = (Math.cos(2 * Math.PI * (order/self.numberOfTopics)) * self.skew) + (self.width/2);
            var y = (Math.sin(2 * Math.PI * (order/self.numberOfTopics)) * self.skew) + (self.width/2);
            var line = createLine(x,y,2 * Math.PI * (order/self.numberOfTopics),110,colorObject);
            self.shapesLayer.add(line);
            // add new circle to shapesLayer
            var circle = createCircle(x,y,colorObject,self.radiusTopic,percentage);
            self.shapesLayer.add(circle);

            var textobj = createText(num_q.toString() + " Q",x,y+25,8);

            var imageObj = new Image();
            imageObj.onload = function()
            {
                var image = new Kinetic.Image
                ({
                    x: x-17,
                    y: y-16,
                    image: imageObj,
                    width: 35,
                    height: 35,
                    zIndex:10
                });

                image.on("mouseover", function()
                {
                    self.hoverShape = createHover(x,y-15); self.hoverLayer.add(self.hoverShape);
                    self.hoverText = createText(Math.round(percentage*100) + "%", x,y-35,10); self.hoverLayer.add(self.hoverText);
                    self.hoverLayer.draw();
                    circle.mouseOver();
                    self.textLayer.add(textobj);
                    self.textLayer.draw();
                    self.shapesLayer.draw();
                    self.imagesLayer.draw();
                });

                image.on('mouseout',function()
                {
                    self.hoverLayer.remove(self.hoverShape);
                    self.hoverLayer.remove(self.hoverText);
                    self.hoverLayer.draw();
                    circle.mouseOut();
                    self.textLayer.remove(textobj);
                    self.textLayer.draw();
                    self.shapesLayer.draw();
                    self.imagesLayer.draw();
                });
                self.imagesLayer.add(image);
                self.imagesLayer.draw();
            };
            imageObj.src = imgRef;
            //self.textLayer.add(createText(num_q.toString(),x,y+self.radiusTopic+14,8));
        });
    },

    /**
     * Helper method to add all the layers to the stage.
     */
    addLayers: function()
    {
        var self = this;
        self.stage.add(self.shapesLayer);
        self.stage.add(self.imagesLayer);
        self.stage.add(self.textLayer);
        self.stage.add(self.hoverLayer);
    }
});

/**
 * Main Load Function for profiles/networks
 */
function loadProfileComparison()
{
    var comparison = new VisualComparison('qaweb',comparisonJSON);
    comparison.draw();
}

/**
 * Function to generate a KineticJS circle object used in comparisons
 *
 * @param x                     x center position
 * @param y                     y center position
 * @param colorObject           object with properties {default:<hex>,light:<hex>}
 * @param radius                radius of circle
 * @param percentage            percentage to fill circle (0<=p<=1)
 * @return Kinetic.Shape
 */
function createCircle(x, y, colorObject, radius, percentage)
{
    return new Kinetic.Shape
    ({
        fill:colorObject.light,
        stroke: colorObject.default,
        radius: radius,
        strokeWidth:2,
        zIndex:10,
        mouseOver:function()
        {
            this.radius = this.radius + 5;
        },
        mouseOut:function()
        {
            this.radius = this.radius - 5;
        },
        drawFunc: function()
        {
            var ctx = this.getContext();
            ctx.zIndex = this.zIndex;

            ctx.beginPath();
            ctx.arc(x,y,this.radius,0,2*Math.PI,false);
            ctx.closePath();
            ctx.fillStyle = "#FFFFFF";
            ctx.fill();

            ctx.beginPath();
            var startAngle = Math.asin(1-(2*percentage));
            var endAngle = Math.PI - startAngle;
            ctx.arc(x,y,this.radius,startAngle,endAngle,false);
            ctx.closePath();
            ctx.fillStyle = this.fill;
            ctx.fill();

            ctx.beginPath();
            ctx.arc(x,y,this.radius,0,2*Math.PI,false);
            ctx.closePath();
            ctx.strokeStyle = this.stroke;
            ctx.stroke();
        }
    });
}

function createBoxPercent(x,y,width,height,colorObject)
{
    return new Kinetic.Rect
    ({
        x:x,
        y:y,
        width:width,
        height:height,
        stroke: colorObject.default,
        fill: colorObject.light,
        zIndex:10
    });
}

function createLine(x,y,rotation,length,colorObject)
{
    return new Kinetic.Rect
    ({
        x:150,
        y:150,
        height:1,
        width:length,
        rotation:rotation,
        stroke: colorObject.default,
        fill: colorObject.light,
        strokeWidth: 1,
        zIndex:3
    });
}

/**
 * Function to generate a KineticJS text object
 *
 * @param string                the string to draw
 * @param x                     the x position
 * @param y                     the y position
 * @param fontSize              fontSize of text
 * @return {Kinetic.Text}
 */
function createText(string,x,y,fontSize)
{
    return new Kinetic.Text
    ({
        text:string,
        fontSize:fontSize,
        fontFamily:"Gill Sans Std Light",
        textFill:"black",
        x:x,
        y:y,
        align:"center",
        verticalAlign:"middle"
    });
}

/**
 * Function to generate a KineticJS custom hover object
 *
 * @param x
 * @param y
 * @return {Kinetic.Shape}
 */
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
            context.strokeStyle = this.stroke;
            context.fillStyle = this.fill;
            context.fill();
            context.stroke();
        },
        fill: "#FFFFFF",
        stroke: "#4d8695",
        strokeWidth: 1
    });
}
