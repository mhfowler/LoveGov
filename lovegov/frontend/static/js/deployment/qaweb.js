var QAWeb = Class.extend
    ({
        // CONSTRUCTOR
        init: function(rootNode)
        {
            this.nodeCount = 0;
            this.nodeList = new Array();
            this.root = rootNode;
            this.selectedQuestion = null;

            this.progressCanvas = new Kinetic.Stage('progress-canvas-div',$('#progress-canvas-div').width(),$('#progress-canvas-div').height());
            this.circleLayer = new Kinetic.Layer();
            this.imageLayer = new Kinetic.Layer();
            this.progressCanvas.add(this.circleLayer);
            this.progressCanvas.add(this.imageLayer);
            this.circleRadius = 30;
        },

        updateProgress: function(state, parentTopic)
        {
            var divWidth = $('#topic_progress_fill').width();
            var currentWidth = $('#topic_progress_fill div').width();
            var delta = Math.ceil(divWidth/this.getNodeCount());
            if (state == -1)
            {
                $('#topic_progress_fill div').width(currentWidth-delta);
            }
            else
            {
                $('#topic_progress_fill div').width(currentWidth+delta);
            }

            var colorObj = {'default':parentTopic.color['default'],'light':parentTopic.color['hover']};
            if (parentTopic.kineticCircle != null) { qaweb.circleLayer.remove(parentTopic.kineticCircle) }
            var answered = 0;
            var childrenSize = parentTopic.children.length;
            for (var i = 0; i< childrenSize; i++)
            {
                if (parentTopic.children[i]._checkAnswered())
                {
                    answered++;
                }
            }

            var x = $('#progress-canvas-div').width()/2;
            var y = (parentTopic.order*this.circleRadius*2.3)+this.circleRadius+5;

            parentTopic.kineticCircle = createCircle(x,y,colorObj,this.circleRadius,answered/childrenSize);
            qaweb.circleLayer.add(parentTopic.kineticCircle);

            this.circleLayer.draw();
            var self = this;


            var imageObj = new Image();
            imageObj.onload = function()
            {
                var image = new Kinetic.Image
                ({
                    x: x-17,
                    y: y-17,
                    image: imageObj,
                    width: 35,
                    height: 35,
                    zIndex:10
                });
                self.imageLayer.add(image);
                self.imageLayer.draw();
            };
            imageObj.src = parentTopic.imgref['mini'].src;
        },


        // PUBLIC METHODS
        toDisplay: function()
        {
            this.root.toDisplay();
            for (var j = 0; j<this.getNodeCount(); j++)
            {
                if (this.nodeList[j] instanceof Question && this.nodeList[j]._checkAnswered())
                {
                    this.updateProgress(1, this.nodeList[j].parents);
                }
            }
        },

        addNode: function(node)
        {
            this.nodeList.push(node);
            this.nodeCount++;
        },

        getNodeCount: function()
        {
            return this.nodeCount;
        }
    });

var QAWebHover = Class.extend
    ({
        init: function()
        {
            this.questionArray = new Array();
            this.node = null;
            this.state;
            this.lastParent = null;
            this.position = null;
            this.idDiv = '#qawebhover';
            this.hoverTimer = false;
            this.$_hover();
        },
        $_hover: function()
        {
            var self = this;
            $(this.idDiv).bind('mouseenter',function()
            {
                clearTimeout(self.hoverTimer);
            });
        },
        updatePosition: function()
        {
            if (this.node != null)
            {
                this._setPosition();
            }
        },


        //TODO fix underanswering questions
        _saveAnswer: function()
        {
            var self = this;

            if ($.trim( $('#answers-ul').html() ).length)
            {
                self.node.weight = $('#weight-input').val();
                var $input = $('#answers-ul').find('input:checked');

                for (var i=0; i<self.node.answers.length; i++)
                {
                    if (self.node.answers[i].answer_value == $input.val())
                    {
                        self.node.answers[i].weight = self.node.weight;
                    }
                }
                var data = self._arrayToDictionary(".qaweb-answerform");
                self.node.user_explanation = data['explanation'];
                if (data.hasOwnProperty('choice'))
                {
                    ajaxPost({data:data,success:null,error:null});
                }
            }
        },

        hide: function()
        {
            var self = this;
            if (self.node != null && !self.node.clicked)
            {
                self._saveAnswer();
                self._toggleButtons('hide');
                self.node = null;
                $('#answers-ul').empty();
                $('._topic_label').hide();
                $('#value_statement').hide();
                $('#question-weight-div').hide();
                $(self.idDiv).fadeOut(10);
            }
        },
        showHover: function(node)
        {
            if (this.node == null || !this.node.clicked)
            {
                this.node = node;
                clearTimeout(this.hoverTimer);
                this._showDiv();
                this._printQuestion();
                this._setInputQID();
                this._setDiscussLink();
                this._setUserExplanation();
                this._setPosition();
                this._setColors();
                $(this.idDiv).fadeIn(100);
            }
        },

        showAnswers: function(node)
        {
            $('#question-weight-div').show();
            this._printAnswers();
            $('#value_statement').show();
            this._bindAnswers();
            this._setPosition();
        },

        _showDiv: function()
        {
            $('#answer-div').show();
            $('#answer-reply').hide();
        },

        _printQuestion: function()
        {
            $('#question').html(this.node.text);
        },

        _setInputQID: function()
        {
            $('#q_id').val(this.node.id);
        },

        _setDiscussLink: function()
        {
            var linkID = this.node.id;
            $('.discuss').attr('href','/question/' + linkID + '/');
        },

        _setUserExplanation: function()
        {
            $('#user_explanation').val(this.node.user_explanation.toString());
        },

        _setPosition: function()
        {
            var position = $(this.node.idDivObj).offset();
            position.left+=$(this.node.idDivObj).width()/2;
            position.left-=($(this.idDiv).width()/2);

            var pointer = $('#dialogue-pointer').detach();
            // FIND SPACE TO FIT VERTICALLY
            if (position.top-$(this.idDiv).height()-30 < 0)
            {
                this.state = "BOTTOM";
                $('.dialogue-wrapper').prepend(pointer);
                $('#dialogue-pointer').css('top','3px');
                $('#dialogue-pointer img').css({'-webkit-transform': 'rotate(180deg)','-moz-transform': 'rotate(180deg)','-ms-transform':'rotate(180deg)','-o-transform':'rotate(180deg)'});
                position.top+=$(this.node.idDivObj).height();
            }
            else
            {
                this.state = 'TOP';
                $('.dialogue-wrapper').append(pointer);
                $('#dialogue-pointer').css('top','-3px');
                $('#dialogue-pointer img').css({'-webkit-transform': 'rotate(0deg)','-moz-transform': 'rotate(0deg)','-ms-transform':'rotate(0deg)','-o-transform':'rotate(0deg)'});
                position.top-=$(this.idDiv).height();
            }
            this.position = position;


            if ($("#first_user").length)
            {
                var first_user = $("#first_user");
                var offset = first_user.offset();
                if (position.top <= offset.top + first_user.height() &&
                    (
                        (position.left + $(this.idDiv).width() >= offset.left && position.left < offset.left + first_user.width()) ||
                        (position.left <= offset.left && first_user.data('state') == "left")
                    )
                    )
                {
                    if (first_user.data('state') == "left")
                    {
                        offset.left+=626;
                        first_user.data('state','right');
                    }
                    else
                    {
                        offset.left-=626;
                        first_user.data('state','left');
                    }
                }
                first_user.offset(offset);

            }

            $(this.idDiv).css(this.position);
        },

        _setColors: function()
        {
            var color = this.node.color;
            $('#question-weight-slider').css('background',color['default']);
            $('#dialogue-main').css("border-color",color['default']);
            $('#dialogue-pointer img').attr('src',color['pointerImage'].src);
            $('.dialogue-buttons').css('backgroundColor',color['default']);
            $('.dialogue-buttons').hover
            (
                function()
                {
                    $(this).css('backgroundColor',color['hover']);
                },
                function()
                {
                    $(this).css('backgroundColor',color['default']);
                }
            );
            $('#user_explanation').css('outline-color',color['hover']);
            $('#user_explanation').css('border','2px solid ' + color['hover']);

        },

        _toggleButtons: function(switchString)
        {
            switch(switchString)
            {
                case 'hide':
                    $('#qa-buttons').hide();
                    break;
                case 'show':
                    $('#qa-buttons').show();
                    break;
            }
        },

        _printAnswers: function()
        {
            var self = this;
            $('#answers-ul').empty();
            $('#answers-ul p').removeClass('answer-selected');
            for (var i=0; i<this.node.answers.length; i++)
            {
                var input = "<input style='display:none' type=radio name='choice' value='" + this.node.answers[i].answer_value + "'/>";
                $('#answers-ul').append('<p class="answer-' + i + '">' + input + this.node.answers[i].answer_text + '</p>');

                if (this.node.answers[i].user_answer)
                {
                    this.node.weight =  this.node.answers[i].weight;
                    $('.answer-' + i + ' input').attr("checked", true);
                    $('.answer-' + i).addClass('answer-selected');
                }
            }

            self._moveSlider(this.node.weight);
        },

        _moveSlider: function(value)
        {
            $("#question-weight-slider").slider("option","value",value);
            $('#weight-input').val(value);
            value = 0.25 + (0.075 * value);
            $('#question-weight-slider').css({opacity:value});
        },

        _bindAnswers: function()
        {
            var self = this;
            var color = this.node.color;
            $('#answers-ul p').hover
            (
                function()
                {
                    if (!$(this).hasClass('answer-selected')) { $(this).css({'background-color':'#EBEBEB',color:'#000000'}); }
                },
                function()
                {
                    if (!$(this).hasClass('answer-selected')) { $(this).css({'background-color':'#FFFFFF',color:'#959595'}); }
                }
            );

            $('#question-weight-slider').unbind("slidechange");
            $('#question-weight-slider').bind("slide", function(event, ui)
            {
                if ($('.step-three').length)
                {
                    var topicSelected = $('.step-three');
                    topicSelected.removeClass("step-three").addClass("step-four");
                    topicSelected.children('p').text("Click an answer to define your stance on this question.");
                    var offset = $('.answer-1').offset();
                    offset.top-=(topicSelected.height()/2);
                    offset.left = topicSelected.offset().left;
                    topicSelected.offset(offset);
                    stepFour();
                }
                var value = parseInt(ui.value);
                self._moveSlider(value);
                self.node.weight = value;
            });


            $('#next_button').unbind('click');
            $('#next_button').bind('click',function(event)
            {
                event.preventDefault();
                var index = $.inArray(self.node,self.questionArray) + 1;
                if (index == self.questionArray.length - 1) { index = 0 }

                var question = self.questionArray[index];
                if (!question.parents.clicked)
                {
                    question.parents._click();
                }
                if (self.lastParent != null && question.parents !== self.lastParent)
                {
                    self.lastParent._click();
                }

                self.lastParent = question.parents;
                self.toggleQuestion(question);

            });

            $('#answers-ul p').click(function()
            {
                if ($('#answers-ul').find('input:checked').length) { var alreadyAnswered = true; }
                if ($(this).children('input').attr("checked")) { var currentAnswer = true; }

                $('#answers-ul p').children('input').attr('checked',false);
                $('#answers-ul p').removeClass("answer-selected").css("background-color",'white').css("color","#959595");

                if (!currentAnswer)
                {
                    var $input = $(this).children('input');
                    $input.attr("checked","checked");
                    $(this).addClass('answer-selected').css("background-color",'#EBEBEB').css("color","black");
                    var data = self._arrayToDictionary(".qaweb-answerform");
                    self.node.HTML_selectRadioAnswer(data['choice']);
                    self.node.onAnswer();
                    if (!alreadyAnswered) {   qaweb.updateProgress(1,self.node.parents); }
                }
                else
                {
                    $(this).removeClass('answer-selected');
                    self.node.onUnAnswer();
                    for (var j=0; j<self.node.answers.length; j++)
                    {
                        self.node.answers[j].user_answer = false;
                    }
                    qaweb.updateProgress(-1,self.node.parents);
                }

                if ($('.step-four').length)
                {
                    var stepDiv = $('.step-four');
                    var offset = $('#next_button').offset();
                    stepDiv.children('p').text("Click the nex to save your answer and go to the next question.");
                    offset.left-= stepDiv.width()+25;
                    offset.top-=4;
                    $('.step-four').addClass("step-five").removeClass("step-four").offset(offset);
                    $('#next_button').bind("click.step_five",function()
                    {
                        $(this).unbind("click.step_five");
                        $('.step-five').remove();
                        stepSix();
                    });
                    stepFive();
                }

                self._saveAnswer();
                $('#answer-saved').show();
                $('#answer-saved').fadeOut(3000);


                /*
                $.ajax
                    ({
                        type: 'POST',
                        url:'/answer/',
                        data: data,
                        success: function(data)
                        {

                            if (!currentAnswer)
                            {
                                // handle drawing on canvas and repositioning
                                var dataObj = eval('(' + data+ ')');
                                $('#dialogue-loading').hide();
                                $('#answer-reply-text span').text((dataObj['answer_avg']*100).toFixed() + '%' + " of LoveGov users agree with you.");

                                var height = $('#answer-reply-canvas').height();
                                var width = $('#answer-reply-canvas').width();

                                stage.setSize(width,height);
                                stage.draw();
                                $('#answer-reply').css('display','block');
                                $('#answer-reply-canvas canvas').css('display','block');

                                if (circle != null && text != null)
                                {
                                    shapesLayer.remove(circle);
                                    shapesLayer.remove(text);
                                    shapesLayer.draw();
                                }

                                for (var i=0; i<self.node.answers.length; i++)
                                {
                                    if (self.node.answers[i].user_answer) { self.node.answers[i].weight = $("#question-weight-slider").slider("option","value");}
                                }

                                circle = createWebCircle(width/2,height/2,75,dataObj['answer_avg'],self.node.color['default'],self.node.color['hover']);
                                shapesLayer.add(circle);
                                text = createText((dataObj['answer_avg']*100).toFixed() + '%',width/2,height/2,14);
                                shapesLayer.add(text);
                                shapesLayer.draw();
                                self.updatePosition();
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown)
                        {
                            alert("failure");
                        }
                    });*/

            });
        },

        _arrayToDictionary: function(selector)
        {
            var objectArray = $(selector).serializeArray();
            var toReturn = {};
            for (var i=0; i<objectArray.length; i++)
            {
                toReturn[objectArray[i].name] = objectArray[i].value;
            }
            toReturn['explanation'] = $('#user_explanation').val();
            toReturn['action'] = "answer";
            return toReturn;
        },

        _clickQuestion: function(node)
        {
            if (node)
            {
                node.clicked = true;
                node.idImgObj.attr("src",node.getImage('answering'));
                this._toggleButtons('show');
                this.showHover(node);
                this.showAnswers(node);
                if (!$('.step-five').length)
                {
                    $('._topic_label').show();
                }

            }
        },

        /**
         * This method handles the user selecting a question.
         *
         * @param node  the node selected by the user
         */
        toggleQuestion: function(node)
        {
            // CASE: user clicks the same question or hasn't clicked a question yet
            if (this.node == null || !this.node.clicked)
            {
                this._clickQuestion(node);
            }
            // CASE: user has a question clicked already and clicks the same question or a different question
            else
            {
                // deselect the current question
                this.node.clicked = false;
                this.node.idImgObj.attr("src",this.node.getImage('default'));
                // CASE: user clicks the same question
                if (this.node == node)
                {
                    this.hide();
                }
                // CASE: user clicks a different question
                else
                {
                    // save current answer data
                    this._saveAnswer();
                    // select new question
                    this._clickQuestion(node);
                }
            }
        }
    });

/**
 * This class represents a graphical node on the QA Web
 * @param   data                    dictionary
 *          xpos (int):             x coordinate offset from left
 *          ypos (int):             y coordinate offset from top
 *          angle (float):          the angle on the unit circle to display this node
 *          ring (int):             the concentric ring number to display this node (1=inner most ring)
 *          imgref (String):        the reference to the image file for this node
 *          parent (int):           used with "ring" to reference parent object in the qaweb
 *          connectColor (String):  the hexadecimal connection color (example: #FFFFFF)
 */
var Node = Class.extend
    ({
        init: function(data)
        {
            this.order = data['order'];
            /**
             * Set Attributes
             */
                // ID TAGS
            this.idnum = qaweb.getNodeCount();
            this.idDiv = 'qadiv' + this.idnum;
            this.idImg = 'qaimg' + this.idnum;
            this.idDivObj = null;
            this.idImgObj = null;

            // HTML/CSS
            this.angle = data['angle'];
            this.ring = data['ring'];
            this.xpos = Math.floor(data['xpos']);
            this.ypos = Math.floor(data['ypos']);
            this.skew = data['skew'];

            // IMAGES REFERENCES
            this.imgref = data['imgref'];

            // LINK INFO
            this.childrenData = data['childrenData'];
            this.children = new Array();
            this.parents = data['parents'];
            this.color = data['color'];
            this.connectLineWidth = 4;
            this.connection = null;

            this.clicked = data['clicked'];

            this.clickEnabled = true;

            this.width;
            this.height;
            this.base_height;
            this.base_width;
        },

        toDisplay: function()
        {
            this.HTML_createNodeDiv(this);
            this.CANVAS_connectParent(this);
            qaweb.addNode(this);
            this.parseChildrenData();
        },

        rePaint: function()
        {
            var self = this;
            // adjust width/height of div/img
            self.idDivObj.css({width:self.width,height:self.height});
            self.idImgObj.css({width:self.width,height:self.height});
            // adjust positioning
            if (self.parents != null)
            {
                if (self.parents.clicked)
                {
                    self.idDivObj.css({left:self.xpos,top:self.ypos});
                }
                else
                {
                    var xpos = self.parents.xpos + (self.parents.width/4);
                    var ypos = self.parents.ypos + (self.parents.height/4);
                    self.idDivObj.css({left:xpos,top:ypos});
                }
            }
            jsPlumb.repaint(self.idDiv);
        },

        parseChildrenData: function()
        {
            if (this.ring==0)
            {
                var n = 7;
                for (var i=0;i<7;i++)
                {
                    var angle = 2 * Math.PI * (i/n);
                    var xpos = (Math.cos(angle) * skew)+this.xpos+11;
                    var ypos = (Math.sin(angle) * skew)+this.ypos+13;
                    var topic = new Topic
                        ({
                            order:i,
                            xpos:xpos,
                            ypos:ypos,
                            angle:angle,
                            skew:skew,
                            ring:this.ring+1,
                            clicked:false,
                            childrenData:assignQuestionTopic(i),
                            parents:this,
                            imgref:topicSwitch(i),
                            text:assignTopicText(i),
                            color:colorSwitch(i)
                        });
                    this.children.push(topic);
                    topic.toDisplay();
                }
            }
            else
            {
                var halfChildrenNum = (this.childrenData.length)/2;

                var step = 1/(this.childrenData.length);
                var angleOffset = -(halfChildrenNum * step);

                for (var j=0; j<this.childrenData.length;j++)
                {
                    var offsetxx = this.xpos;
                    var offsetyy = this.ypos;
                    if (j%2==0)
                    {
                        var newskew = (this.ring+1)*(180 + (this.ring*50));
                    }
                    else
                    {
                        var newskew = (this.ring+1)*(125 + (this.ring*50));
                    }

                    var angle2 = this.angle + angleOffset + (step*j);
                    var xpos2 = (Math.cos(angle2) * newskew)+offsetxx;
                    var ypos2 = (Math.sin(angle2) * newskew)+offsetyy;
                    var test = new Question
                    ({
                        xpos:xpos2,
                        ypos:ypos2,
                        angle:angle2,
                        skew:newskew,
                        ring:this.ring+1,
                        imgref:questionSwitch(this.order),
                        parents:this,
                        color:this.color,
                        childrenData:this.childrenData[j]['childrenData'],
                        text:this.childrenData[j]['text'],
                        answers:this.childrenData[j]['answers'],
                        id:this.childrenData[j]['id'],
                        user_explanation:this.childrenData[j]['user_explanation']
                    });
                    test.toDisplay();
                    this.children.push(test);
                    test._init_hide();
                }
            }
        },


        _init_hide: function()
        {
            var self = this;
            self.idDivObj.css({left:self.parents.xpos+25,top:self.parents.ypos+25});
            jsPlumb.repaint(self.idDiv);
            self.idDivObj.unbind();
        },


        _init_drawConnection: function()
        {
            var self = this;
            return jsPlumb.connect
            ({
                source:self.idDiv,
                target:self.parents.idDiv,
                anchor:[0.5, 0.5, 0.5, 0.5],
                connector:["Straight"],
                paintStyle:{strokeStyle:self.color['default'], lineWidth:self.connectLineWidth * ZOOM},
                endpoint:["Rectangle", { width:1, height:1 }]
            });
        },

        /**
         * This method generates the HTML div that houses the node
         */
        HTML_createNodeDiv: function()
        {
            var self = this;
            var left = 'left:' + self.xpos + "px;";
            var top = 'top:' + self.ypos + "px;";
            var zindex = "z-index:50;";
            var style = 'style="position:absolute;' + left + top + zindex +'"';
            $(DRAGGER_ID).append("<div class='node' id='" + self.idDiv + "' " + style + "></div>");
            self.idDivObj = $('#' + self.idDiv);
        },

        /**
         * This method zooms and resizes a node and all of its children
         */
        zoomResize: function()
        {
            var self = this;

            // adjust x/pos position and height/width for zoom
            self.xpos = (Math.cos(self.angle) * self.skew * ZOOM) + self.parents.xpos+(11*ZOOM);
            self.ypos = (Math.sin(self.angle) * self.skew * ZOOM) + self.parents.ypos+(13*ZOOM);
            self.width = self.base_width * ZOOM;
            self.height = self.base_height * ZOOM;


            if (self instanceof Topic)
            {
                var div= $('#' + self.text.replace(" ","") + '_label');
                var xpos = (Math.cos(self.angle) * (self.skew+(div.width()/3)) * ZOOM) + self.xpos-10;
                var ypos = (Math.sin(self.angle) * (self.skew-div.height()) * ZOOM) + self.ypos + div.height()/2;
                $('#' + self.text.replace(" ","") + '_label').css({left:xpos,top:ypos});
            }


            // repaints jsplumb connectors
            if (self.connection != null)
            {
                self.connection.setPaintStyle({strokeStyle:self.color['default'], lineWidth:self.connectLineWidth*ZOOM});
            }
            self.rePaint();

            // cursively zoomResize children nodes
            for (var i=0; i<self.children.length; i++)
            {
                self.children[i].zoomResize(self.children[i]);
            }
        },

        /**
         * This method uses jsPlumb to connect this node to its parent node
         * @param self
         */
        CANVAS_connectParent: function()
        {
            var self = this;
            if (self.parents != null)
            {
                self.connection = self._init_drawConnection();
            }
        },

        /**
         * Assigns onClick functionality to this node via jQuery selector
         * @param self  reference to this
         */
        $_onClick: function()
        {
            var self = this;
            this.idImgObj.bind('click',function()
            {
                if (self.clickEnabled)
                {
                    self._click();
                }
            });
        },

        /**
         * Assigns onHover functionality to this node via jQuery selector
         * @param self  reference to this
         */
        $_onHover: function()
        {
            var self = this;
            self.idImgObj.bind('mouseenter',function()
            {
                $(this).css('cursor','pointer');
                self._mouseEnter();
            });
            self.idImgObj.bind('mouseleave',function()
            {
                self._mouseLeave();
            });
        },

        _expand: function()
        {
            var self = this;
            self.clickEnabled = false;
            // recursive expand this node's children and connect each child to this node
            for (var i=0; i<self.children.length;i++)
            {
                self.children[i].ANIMATE_show();
                self.children[i]._expand();
            }
            self.clickEnabled = true;
        },
        _collapse: function()
        {
            var self = this;
            self.clickEnabled = false;
            // recursive collapse this node's children and remove the connection from each child to this node
            for (var i=0; i<self.children.length;i++)
            {
                self.children[i].ANIMATE_hide();
                self.children[i]._collapse();
            }
            self.clickEnabled = true;
        },

        ANIMATE_hide: function()
        {
            var self = this;
            var duration  = 250;
            var xpos = self.parents.xpos + (self.parents.width/4);
            var ypos = self.parents.ypos + (self.parents.width/4);
            self.idDivObj.animate({left:xpos,top:ypos},{duration:duration,step: function(now, fx)
                {
                    jsPlumb.repaint(self.idDiv);
                }}
            );
            setTimeout(function(){jsPlumb.repaint(self.idDiv);},750);
            self.idImgObj.unbind();
        },
        ANIMATE_show: function()
        {
            var self = this;
            self.idDivObj.css('visibility','visible');
            self.idDivObj.animate({left:self.xpos,top:self.ypos},{duration:250,step: function(now, fx)
                {
                    jsPlumb.repaint(self.idDiv);
                    qaWebHover.updatePosition();
                }, complete: function(){  qaWebHover.updatePosition();}}
            );
            setTimeout(function(){jsPlumb.repaint(self.idDiv);},250);
            this.$_onClick();
            this.$_onHover();
        }
    });



/**
 *
 */
var Question = Node.extend
    ({
        init: function(data)
        {
            this.base_width = 50;
            this.base_height = 50;
            this.width = 50;
            this.height = 50;
            this.text = data['text'];
            this.id = data['id'];
            this.weight = 5;
            this.answers = data['answers'];
            this.answered = this._checkAnswered();
            this.user_explanation = data['user_explanation'];
            this._super(data);
            qaWebHover.questionArray.push(this);
        },

        toDisplay: function()
        {
            this._super();
            this.idDivObj.css('visibility','hidden');
            this.HTML_appendImg();
        },

        onAnswer: function()
        {
            this.answered = true;
            if (this.clicked)
            {
                this.idImgObj.attr("src",this.getImage('answering'));
            }
            else
            {
                this.idImgObj.attr("src",this.getImage('default'));
            }
        },

        onUnAnswer: function()
        {
            this.answered = false;
            if (this.clicked)
            {
                this.idImgObj.attr("src",this.getImage('answering'));
            }
            else
            {
                this.idImgObj.attr("src",this.getImage('default'));
            }
        },

        /**
         * This method generates the HTML div that houses the node
         * @param self          reference to "this"
         */
        HTML_createNodeDiv: function()
        {
            var self = this;
            var left = 'left:' + self.xpos + "px;";
            var top = 'top:' + self.ypos + "px;";
            var zindex = "z-index:50;";
            var width = "width:50px;";
            var height = "height:50px;";
            var style = 'style="position:absolute;' + left + top + zindex + width + height + '"';
            $(DRAGGER_ID).append("<div class='_question' id='" + self.idDiv + "' " + style + "></div>");
            this.idDivObj = $('#' + this.idDiv);
        },

        HTML_appendImg: function()
        {
            var self = this;
            var src = 'src="' + self.getImage('default') + '"';
            var style = 'style="position:absolute;"';
            $('#' + self.idDiv).append("<img class='question-node-img' id='" + self.idImg + "' " + src + style + " " + "/>");
            this.idImgObj = $('#' + this.idImg);
        },

        HTML_selectRadioAnswer: function(answer_val)
        {
            for (var i=0; i<this.answers.length; i++)
            {
                this.answers[i].user_answer = (this.answers[i].answer_value == answer_val);
            }
        },

        _checkAnswered: function()
        {
            for (var i=0; i<this.answers.length;i++)
            {
                if (this.answers[i].user_answer)
                {
                    return true;
                }
            }
            return false;
        },

        getImage: function(state)
        {
            switch(state)
            {
                case 'hover':
                    if (this.answered) return this.imgref['answeredHover'].src;
                    else return this.imgref['unansweredHover'].src;
                    break;
                case 'default':
                    if (this.answered) return this.imgref['answeredDefault'].src;
                    else return this.imgref['unansweredDefault'].src;
                    break;
                case 'answering':
                    if (this.answered){ return this.imgref['answeredAnswering'].src; }
                    else{ return this.imgref['unansweredAnswering'].src; }
                    break;
            }
        },

        // UI FUNCTIONALITY
        _click: function()
        {
            var self = this;
            qaWebHover.toggleQuestion(this);

            var topicSelected;
            if ($('.step-two').length)
            {
                var offset = $('#question-weight-div span').offset();
                offset.left-=250;
                offset.top-=10;
                topicSelected = $('.step-two').detach();
                $('#qawebhover').append(topicSelected);
                topicSelected.offset(offset);
                var pointer = '<div class="label-pointer"><div class="border"></div><div class="inner"></div></div>';
                topicSelected.html("<p class='no-margin'>How important is this question to you? Adjust the slider accordingly.</p>");
                topicSelected.append(pointer);
                topicSelected.children(".label-pointer").children(".border").css("border-color",'transparent transparent transparent ' + self.color.default);
                topicSelected.children(".label-pointer").children(".inner").css("border-color",'transparent transparent transparent ' + self.color.default);
                topicSelected.removeClass("step-two").addClass("step-three");
                stepThree();
            }

            if ($('.step-three').length)
            {
                topicSelected = $('.step-three');
                var offset = $('#question-weight-div span').offset();
                offset.left-=250;
                offset.top-=10;
                topicSelected.offset(offset);
                topicSelected.css("background-color",self.color.default);
                topicSelected.children(".label-pointer").children(".border").css("border-color",'transparent transparent transparent ' + self.color.default);
                topicSelected.children(".label-pointer").children(".inner").css("border-color",'transparent transparent transparent ' + self.color.default);
            }

            if ($('.step-four').length)
            {
                topicSelected = $('.step-four');
                var offset = $('.answer-1').offset();
                offset.top-=(topicSelected.height()/2);
                offset.left = topicSelected.offset().left;
                topicSelected.offset(offset);
                topicSelected.css("background-color",self.color.default);
                topicSelected.children(".label-pointer").children(".border").css("border-color",'transparent transparent transparent ' + self.color.default);
                topicSelected.children(".label-pointer").children(".inner").css("border-color",'transparent transparent transparent ' + self.color.default);
            }

        },
        _mouseEnter: function()
        {
            var self = this;
            if (!self.clicked)
            {
                qaWebHover.showHover(self);
                self.idImgObj.attr("src",self.getImage('hover'));
            }
        },
        _mouseLeave: function()
        {
            var self = this;
            if (!self.clicked)
            {
                qaWebHover.hide();
                self.idImgObj.attr("src",self.getImage('default'));
            }
        }

    });

var Topic = Node.extend
    ({
        init: function(data)
        {
            this.base_width = 100;
            this.base_height = 100;
            this.width = 100;
            this.height = 100;
            this.text = data['text'];
            this.kineticCircle = null;
            this._super(data);

        },

        toDisplay: function()
        {
            this._super();
            this.HTML_appendImg(this);
            this.$_onClick(this);
            this.$_onHover(this);
        },

        /**
         * Assigns onHover functionality to this node via jQuery selector
         * @param self  reference to this
         */
        $_onHover: function()
        {
            this._super();
            var self = this;
            self.idImgObj.bind('mouseenter',function()
            {
                var position = self.idDivObj.offset();
                position.left-=($('#qawebtopichover').width()/2);
                position.left+=(self.idDivObj.width()/2);
                position.top-=$('#qawebtopichover').height();
                position.top+=5;
                $('#topic-main').css('border-color',self.color['default']);
                $('#topic-pointer img').attr('src',self.color['pointerImage'].src);
                $('#qawebtopichover').css(position);
                $('#topic-text').text(self.text);
                $('#qawebtopichover').fadeIn(10);
            });
            self.idImgObj.bind('mouseleave',function()
            {
                $('#qawebtopichover').fadeOut(10);
            });
        },

        HTML_createNodeDiv: function(self)
        {
            var self = this;
            var left = 'left:' + self.xpos + "px;";
            var top = 'top:' + self.ypos + "px;";
            var zindex = "z-index:60;";
            var size = "width:" + this.base_width + "px; height:" + this.base_height + "px;";
            var style = 'style="position:absolute;' + left + top + zindex + size + '"';
            $(DRAGGER_ID).append("<div class='_topic' id='" + self.idDiv + "' " + style + "></div>");

            var color = "background-color:" + this.color.default + ";color:white";
            left = 'left:' + self.xpos + "px;";
            var label_style = 'style="display:none;position:absolute;' + left + top + color + '"';
            $(DRAGGER_ID).append("<div class='_topic_label' id='" + self.text.replace(" ","") + "_label' " + label_style + ">" + self.text + "</div>");

            var colorObj = {'default':this.color['default'],'light':this.color['hover']};

            this.idDivObj = $('#' + this.idDiv);
        },

        HTML_appendImg: function(self)
        {
            var src = 'src="' + self.getImage('default') + '"';
            $('#' + self.idDiv).append("<img id='" + self.idImg + "' " + src + " " + "/>");
            this.idImgObj = $('#' + this.idImg);
        },

        getImage: function(state)
        {
            switch(state)
            {
                case 'default':
                    return this.imgref['default'].src;
                    break;
                case 'hover':
                    return this.imgref['hover'].src;
                    break;
                case 'selected':
                    return this.imgref['selected'].src;
                    break;
            }
        },

        _mouseEnter: function()
        {
            var self = this;
            if (!self.clicked)
            {
                self.idImgObj.attr("src",self.getImage('hover'));
            }
        },
        _mouseLeave: function()
        {
            var self = this;
            if (!self.clicked)
            {
                self.idImgObj.attr("src",self.getImage('default'));
            }
        },
        _click: function()
        {
            var self = this;
            if ($('.step-one').length)
            {
                $('._topic_label').each(function()
                {
                    if ($(this).attr('id').replace("_label","") != self.text.replace(" ","")) { $(this).hide('explode', function(){$(this).remove()}); }
                    else { $(this).removeClass("step-one").addClass("step-two").text("Click a ?");  }
                });
                stepTwo();
            }

            if (self.clicked)
            {
                if (qaWebHover.node != null && qaWebHover.node.parents == this)
                {
                    qaWebHover.toggleQuestion(qaWebHover.node);
                }
                self.clicked = false;
                self.idImgObj.attr("src",self.getImage('default'));
                self._collapse();
            }
            else
            {
                self.clicked = true;
                self.idImgObj.attr("src",self.getImage('selected'));
                self._expand();
            }
        }



    });

/**
 *
 */
var Root = Node.extend
    ({
        init: function(data)
        {
            this._super(data);
            this.xpos = Math.floor(data['xpos']);
            this.ypos = Math.floor(data['ypos']);
            this.base_width = 125;
            this.base_height = 125;
            this.width = 125;
            this.height = 125;
        },
        toDisplay: function()
        {
            this._super();
            this.HTML_appendImg(this);
        },

        HTML_appendImg: function(self)
        {
            var src = 'src="' + "/static/images/you.png" + '"';
            $('#' + self.idDiv).append("<img id='" + self.idImg + "' " + src + " " + "/>");
            this.idImgObj = $('#' + this.idImg);
        },

        HTML_createNodeDiv: function(self)
        {
            var left = 'left:' + self.xpos + "px;";
            var top = 'top:' + self.ypos + "px;";
            var zindex = "z-index:70;";
            var size = "width:" + this.base_width + "px; height:" + this.base_height + "px;";
            var style = 'style="position:absolute;' + left + top + zindex + size + '"';
            $(DRAGGER_ID).append("<div id='" + self.idDiv + "' " + style + "></div>");
            this.idDivObj = $('#' + this.idDiv);
        },
        zoomResize: function(self)
        {
            self.width = self.base_width * ZOOM;
            self.height = self.base_height * ZOOM;
            if (self.connection != null)
            {
                self.connection.setPaintStyle({strokeStyle:self.color['default'], lineWidth:self.connectLineWidth*ZOOM});
            }
            self.rePaint(self);
            for (var i=0; i<self.children.length; i++)
            {
                self.children[i].zoomResize(self.children[i]);
            }
        }

    });


/**
 * Variables
 */

// The ID of the div for the QAWeb
var DRAGGER_ID = '#dragger';
var QAWEB_ID = '#qaweb-interactive';
// Initialize QAWeb
var qaweb = new QAWeb();
// Initialize QAWebHover
var qaWebHover = new QAWebHover();

// KineticJS variables
var stage;
var shapesLayer;
var circle;
var text;

// The path to image files
var IMAGE_DIRECTORY = '/static/images/questionIcons/';

/**
 * QA Web Display Variables
 */

// ZOOM
var ZOOM = 0.6;
var ZOOM_OUT_MAX = 0.6;
var ZOOM_IN_MAX = 1.4;
var ZOOM_STEP = 0.2;

// POSITIONING
var skew = 150;
var draggerWidth = 2600;
var draggerHeight = 2200;
var offsetx = draggerWidth/2;
var offsety = (draggerHeight/2)-100;

/**
 * Function to be called to load QAWeb on page load.
 */
function loadQAWeb()
{
    initializeInitialView();
    initializejsPlumb();
    initializeQAWeb();
    initializeKineticJS($('#answer-reply-canvas').width(),$('#answer-reply-canvas').height());
    initializeDragScroll();
    initializeButtonFunctionality();
    initializeZoomFunctionality();
    qaweb.root.zoomResize(qaweb.root);
    setTimeout(function() {$(QAWEB_ID).scrollTop(offsety - ($(window).height()/2)+62);},150);
    setTimeout(function() {$(QAWEB_ID).scrollLeft(offsetx - ($(window).width()/2)+62);},150);
}

function initializeInitialView()
{
    $('body').css("overflow","hidden");
    $('#main-content').css("top","-48px");
    $(DRAGGER_ID).css('width', draggerWidth + "px");
    $(DRAGGER_ID).css('height', draggerHeight + "px");
    $(QAWEB_ID).css('height',($(window).height() + 'px'));
    $('#qaweb-interactive').css('height',($(window).height()) + 'px');
}

function initializejsPlumb()
{
    jsPlumb.Defaults.Container = $(DRAGGER_ID);
    jsPlumb.setRenderMode(jsPlumb.SVG);
}

function initializeQAWeb()
{
    var root = new Root
    ({
        xpos:offsetx,
        ypos:offsety,
        angle:0,
        ring:0,
        clicked:true,
        childrenData:[],
        imgref:topicSwitch(0),
        parents:null,
        text:"",
        color:colorSwitch(0)
    });
    qaweb = new QAWeb(root);
    qaweb.toDisplay();
}

function initializeKineticJS(width, height)
{
    stage = new Kinetic.Stage("answer-reply-canvas", width, height);
    shapesLayer = new Kinetic.Layer();
    stage.add(shapesLayer);
}

function initializeDragScroll()
{
    // ALLOWS FOR DRAG SCROLL
    $(QAWEB_ID).dragscrollable({dragSelector: DRAGGER_ID, acceptPropagatedEvent:true, preventDefault:false, qaWebHover:qaWebHover});

    // CUSTOM CURSOR IMAGES
    $(DRAGGER_ID).mousedown(function(event)
    {
        event.preventDefault();
        $(this).css('cursor','url(/static/images/cursors/holdcursor.gif),auto');
    });
    $(DRAGGER_ID).mouseup(function(event)
    {
        event.preventDefault();
        $(this).css('cursor','url(/static/images/cursors/grabcursor.gif),auto');
    });

}

function initializeButtonFunctionality()
{
    $("#dialogue-exit-span").click(function(event)
    {
        event.preventDefault();
        qaWebHover.toggleQuestion(qaWebHover.node);
    });

    $('#qawebhover').bind('clickoutside',function(event)
    {
        if (!$('#' + event.target.id).hasClass("question-node-img"))
        {
            qaWebHover.toggleQuestion(qaWebHover.node);
        }

    });
}

function initializeZoomFunctionality()
{
    $(QAWEB_ID).mousewheel(function(objEvent, intDelta)
    {
        objEvent.preventDefault();
        // ZOOM IN
        if (intDelta > 0)
        {
            if (ZOOM < ZOOM_IN_MAX) { ZOOM+=ZOOM_STEP; }
        }
        // ZOOM OUT
        else if (intDelta < 0)
        {
            if (ZOOM > ZOOM_OUT_MAX) { ZOOM-=ZOOM_STEP; }
        }
        qaweb.root.zoomResize(qaweb.root);
        qaWebHover.updatePosition();
    });
}


function assignTopicText(topicID)
{
    switch(topicID)
    {
        case 0:
            return 'Economy';
        case 1:
            return 'Education';
        case 2:
            return 'Energy';
        case 3:
            return 'Environment';
        case 4:
            return 'Health Care';
        case 5:
            return 'National Security';
        case 6:
            return 'Social Issues';
        default:
            return 'Economy';
    }
}

function assignQuestionTopic(topicID)
{
    var topicString = assignTopicText(topicID);
    return questionsArray[topicString];
}

/**
 * This function returns  of images for the three states of each topic image
 *
 * @param topicID integer
 * @return dictionary
 */
function topicSwitch(topicID)
{
    var imageDict = {};
    var types = ['default','hover','selected','mini'];
    var topicString = assignTopicText(topicID).toLowerCase().replace(/\s+/g, '');
    var subname = topicString.substring(0,3).toLowerCase();
    for (var i=0; i<types.length;i++)
    {
        var image = new Image();
        image.src = IMAGE_DIRECTORY + topicString + '/' + subname + "_" + types[i] + ".png";
        imageDict[types[i]] = image;
    }
    return imageDict;
}

function questionSwitch(topicID)
{
    var types = ['Default','Hover','Answering'];
    var states = ['unanswered','answered'];
    var topicString = assignTopicText(topicID).toLowerCase().replace(/\s+/g, '');;
    return makeQuestionImageArray(topicString,states,types);
}

function makeQuestionImageArray(topic,states,types)
{
    var imageDict = {};
    var subname = topic.substring(0,3);
    for (var i=0;i<states.length;i++)
    {
        for (var j=0;j<types.length;j++)
        {
            var image = new Image();
            image.src = IMAGE_DIRECTORY + topic + "/" +  states[i] + "/" + subname + "_" + states[i] + types[j] + ".png";
            imageDict[states[i] + types[j]] = image;
        }
    }
    return imageDict;
}

function colorSwitch(topicID)
{
    var topicString = assignTopicText(topicID).toLowerCase().replace(/\s+/g, '');
    var subname = topicString.substring(0,3);
    var image = new Image();
    image.src =  IMAGE_DIRECTORY + topicString + "/" + subname + "_" + "pointer.png";
    switch(topicID)
    {
        case 0:
            return {'default':"#92B76C",'hover':"#CCDDC0", 'pointerImage':image};
        case 1:
            return {'default':"#9DC5C9",'hover':"#D3EBED", 'pointerImage':image};
        case 2:
            return {'default':"#F9D180",'hover':"#FFF0C5", 'pointerImage':image};
        case 3:
            return {'default':"#9797C6",'hover':"#D4D3EF", 'pointerImage':image};
        case 4:
            return {'default':"#EA7D95",'hover':"#FBCCD6", 'pointerImage':image};
        case 5:
            return {'default':"#EA947D",'hover':"#FFCBC0", 'pointerImage':image};
        case 6:
            return {'default':"#639E9B",'hover':"#A3C6C4", 'pointerImage':image};
        default:
            return {'default':"#FEE1A1",'hover':"#FFF3D9", 'pointerImage':image};
    }
}

function createText(string,x,y,fontSize)
{
    return new Kinetic.Text
        ({
            text:string,
            fontSize:fontSize,
            fontFamily:"Arial",
            textFill:"black",
            x:x,
            y:y,
            align:"center",
            verticalAlign:"middle"
        });
}


function createWebCircle(x, y, radius, percentage, stroke, fill)
{
    return new Kinetic.Shape
        ({
            state: 0,
            radius: radius,
            zIndex:10,
            drawFunc: function()
            {
                // get canvas to draw on
                var ctx = this.getContext("2d");

                // create fill
                ctx.beginPath();
                var startAngle = Math.asin(1-(2*percentage));
                var endAngle = Math.PI - startAngle;
                ctx.arc(x,y,this.radius,startAngle,endAngle,false);
                ctx.closePath();
                ctx.fillStyle = fill;
                ctx.fill();

                // create stroke
                ctx.beginPath();
                ctx.arc(x,y,this.radius,0,2*Math.PI,false);
                ctx.closePath();
                ctx.lineWidth = 2;
                ctx.strokeStyle = stroke;
                ctx.stroke();
            }
        });
}

