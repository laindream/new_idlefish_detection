Java.perform(function () {
    var SwitchConfig = Java.use('mtopsdk.mtop.global.SwitchConfig');
    var description = ""
    var obj = SwitchConfig
    // for (var i in obj) {  
    // 	if(Object.prototype.toString.call(obj[i])=== '[object Function]'){
    // 		//description += i + "{{{{{{{{" + obj[i].toLocaleString() + "}}}}}}}}}}}";
    //    	}
    //    	else{
    //    		var n = obj[i];
    //    		for( var j in n){
    //    			description += i + "{{{{{" + j + "}}}}}"
    //    		}
    //    	}
    	
    //     //description += i + " = " + obj[i] + "\n";  
    // } 
    // send(description)
    SwitchConfig.zm.overload().implementation = function () {
    	send("disable Spdy");
        return false;
    }
});