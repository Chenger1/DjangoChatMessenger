function socket_onmessage(e){
	let data = JSON.parse(e.data);
	let message = data.message;

	let dateOptions = {hour: 'numeric', minute: 'numeric', housr12: true};
	let datetime = new Date(data['created']).toLocaleString('en', dateOptions);

	// Use 'username' to check message`s author and add right class for div
	let isMe = data.user === username;
	let source = isMe ? 'me': 'other';
	let name = isMe ? 'Me': data.user;

	let $chat = document.getElementById('chat');
	let child = document.createElement('div')
	child.innerHTML = '<div class="message '+ source +'">' + 
					  '<strong>' + name + '</strong>' + ' ' +
					  '<span class="date">'+ datetime +'</span><br>' +
					  message + 
					  '</div>';
	$chat.append(child);

	// check children`s 'array' to get last element and his ofsset to scroll 
	let chat_children_length = $chat.children.length;
	let last_element_offset = $chat.children[chat_children_length-1].offsetTop;
	$chat.scrollTop = last_element_offset;
}

function socket_onclose(e){
	console.error('Chat socked closed');
}

function submit_event_listener(e){
	let message = $input.value;
	if(message) {
		// send message in JSON format
		chatSocket.send(JSON.stringify({'message': message}));

		//clear input
		$input.value = '';

		// return focus
		$input.focus();
	}
}

function input_event_listener(e){
	if(e.which === 13){
		$submit.click();
	}
}
