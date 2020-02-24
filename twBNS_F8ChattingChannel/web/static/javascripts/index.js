$(document).ready(function() {
    console.log('hello world');
    if (!('Notification' in window)) {
        console.log('This browser does not support notification');
    }
    else if (Notification.permission === 'default' || Notification.permission === 'undefined') {
      Notification.requestPermission(function(permission) {
        console.log('This browser does support notification');
        console.log(Notification.permission);

      });
    }
    else {
        console.log('Notification.permission allowed?');
        console.log(Notification.permission);
    }
    var MaxInputs    = 18; //maximum input boxes allowed
    var InputsWrapper  = $("#InputsWrapper"); //Input boxes wrapper ID
    var AddButton    = $("#AddMoreFileBox"); //Add button ID
    var StartButton = $("#Start")
    var StopButton = $('#Stop')
    var MaxKeywordGroups = 8;
    var x = InputsWrapper.length; //initlal text box count
    var FieldCount=1; //to keep track of text box added
    var input_keywords = new Array();
    var keywords = new Array();
    var word_filter = ['<', '>', '\\', '/', ',', '.']
    for(var i=0; i<MaxInputs; i++) {
        keywords[i] = new Array();
    }
    var keyword_groups = [0,0,0,0,0,0,0,0];
    var doNotify = false;
    var notify_mid = document.createElement("audio");
    notify_mid.src = "static/notify.ogg";
    var index = 0;
    $(StartButton).attr('disabled', false);
    $(StopButton).attr('disabled', true);
    
    $(StartButton).click(function (e) {

        $("input:text").each(
            function(element) {input_keywords[index] = this.value; index++;}
            );
        
        $(StartButton).attr('disabled', true);
        $(StopButton).attr('disabled', false);
        doNotify = true;
        var groupofword = 0;
        //var prefix = false;
        for(var i=0; i<index; i++) {
            //console.log(input_keywords[i]);
            if(input_keywords[i][0]=='@' && input_keywords[i][1] == '_') {
                var num = parseInt(input_keywords[i][2]);
                //prefix = true;
                keywords[i][0] = input_keywords[i].substring(3, input_keywords[i].length);
                if(num > MaxKeywordGroups || num < 0) {
                    groupofword = 0;
                }
                else {
                    groupofword = num;
                }
            }
            else {
                //prefix = false;
                groupofword = 0;
                keywords[i][0] = input_keywords[i];
            }
            /*
            if(prefix) {
                keywords[i][0] = input_keywords[i].substring(3, input_keywords[i].length);
            }
            else{
                keywords[i][0] = input_keywords[i];
            }
            */
            keywords[i][1] = groupofword;
            keyword_groups[groupofword]++;
        }
        /*
        for(var i=0; i<MaxKeywordGroups; i++) {
            console.log(keyword_groups[i]);
        }
        */

    });

    $(StopButton).click(function (e) {
        index = 0;
        doNotify = false;
        keyword_groups = [0,0,0,0,0,0,0,0];
        keywords = new Array();
        for(var i=0; i<18; i++) {
            keywords[i] = new Array();
        }
        input_keywords = new Array();

        $(StartButton).attr('disabled', false);
        $(StopButton).attr('disabled', true);
    });

    $(function () {
        var $messages = $('.messages-content');

        $(window).load(function () {
            $messages.mCustomScrollbar();
        });


        var namespace = '';
        //var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);
        var socket = io.connect('https://f8.twbns.cf/');
        socket.on('connect', function () {
            //console.log('connected!');
            socket.emit('join', {room: 'A_Room'});
        });

        function updateScrollbar() {
            $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
                scrollInertia: 10,
                timeout: 0
            });
        }

        function setDate(time) {
            $('<div class="timestamp">' + time + '</div>').appendTo($('.message:last'));
        }

        socket.on('getInquiry', function (msg) {
            //console.log("125 index: " + index)
            var newmsg = msg.msg;
            var playername = msg.player;
            var blacklist = false;
            var keyword_matched = [0,0,0,0,0,0,0,0];
            var Notufy_emit = false;

            for(var i=0; i<word_filter.length; i++) {
                if(playername.indexOf(word_filter[i]) != -1) {
                    playername = "";
                }
                if(newmsg.indexOf(word_filter[i]) != -1) {
                    newmsg = "";
                }
            }

            if(doNotify) {
                for(var i=0; i<index; i++) {
                    //console.log(keywords[i][0]);
                    if(playername.indexOf(keywords[i][0]) != -1 && keywords[i][1] == 7) {
                        i = index;
                        blacklist = true;
                    }
                    else if(newmsg.indexOf(keywords[i][0]) != -1) {
                        //console.log("MATCHED!");
                        if(keywords[i][1] == 6) {
                            i = index;
                            blacklist = true;
                        }
                        else {
                            keyword_matched[keywords[i][1]]++;
                        }
                    }
                }

                if(blacklist) {
                    //do nothing
                }
                else {
                    for(var i=0; i<6; i++){
                        if(keyword_matched[i] == keyword_groups[i] && keyword_groups[i] != 0) {
                            Notufy_emit = true;
                            i = 6;
                        }
                    }
                    if(Notufy_emit) {
                        newmsg = '<font color="red"><b>'+ newmsg + '</b></font>';
                        notify_mid.play();
                        //console.log("MATCHED!");
                        if (Notification.permission === 'granted') {
                            var notifyConfig = {
                                body: newmsg+" matched "+keyword, 
                                //icon: '/images/favicon.ico', 
                            };
                            var notification = new Notification("關鍵字出現!!", notifyConfig);
                            notification.onclick = function(e) {
                                e.preventDefault(); // prevent the browser from focusing the Notification's tab
                            }
                        }
                    }
                }
                /*No domain name no ssl certificate, no ssl certificate no notification API
                keywords.forEach(function(keyword, index){
                    console.log('keyword=' + keyword);
                    if(newmsg.indexOf(keyword) != -1 && doloop) {
                        //console.log("MATCHED!");

                        if (Notification.permission === 'granted') {
                            var notifyConfig = {
                                body: newmsg+" matched "+keyword, 
                                //icon: '/images/favicon.ico', 
                            };
                            var notification = new Notification("關鍵字出現!!", notifyConfig);
                            notification.onclick = function(e) {
                                e.preventDefault(); // prevent the browser from focusing the Notification's tab
                            }
                        }

                        //alert("關鍵字出現!! " + newmsg);

                        doloop = false;
                    }
                    else{
                        //console.log("NO");
                    }
                });*/
            }

            $('<div class="message new">' + playername + '：' + newmsg + '</div>').appendTo($('.mCSB_container')).addClass('new');
            setDate(msg.time);
            //$('.message-input').val(null);
            updateScrollbar();
        });


        $('.message-submit').click(function () {
            insertMessage();
        });

        $(window).on('keydown', function (e) {
            if (e.which == 13) {
                insertMessage();
                return false;
            }
        });
    });

    $(AddButton).click(function (e) //on add input button click
    {
    if(x < MaxInputs) { //max input box allowed
    FieldCount++; //text box added increment
    //add input box
    $(InputsWrapper).append('<div><input type="text" name="mytext[]" id="field_'+FieldCount+'" value="Text '+FieldCount+'"/><input type="button" value="刪除" class="removeclass"></div>');
    x++; //text box increment
    }
    return false;
    });
    $("body").on("click",".removeclass", function(e){ //user click on remove text
    if( x > 1 ) {
    $(this).parent('div').remove(); //remove text box
    x--; //decrement textbox
    }
    return false;
    });

});