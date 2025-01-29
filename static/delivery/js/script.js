document.addEventListener('DOMContentLoaded', function () {
	if(document.getElementById('restaurant-photo') != null) {
		document.getElementById('restaurant-photo').addEventListener('change', function (event) {
		  const file = event.target.files[0];
		  if (file) {
			const reader = new FileReader();
			reader.onload = function (e) {
			  document.getElementById('preview-logo').src = e.target.result;
			};
			reader.readAsDataURL(file);
		  }
		});
	  }});

document.addEventListener('DOMContentLoaded', function () {
	if(document.getElementById('item-photo') != null) {
	document.getElementById('item-photo').addEventListener('change', function (event) {
	  const file = event.target.files[0];
	  if (file) {
		const reader = new FileReader();
		reader.onload = function (e) {
		  document.getElementById('preview-logo').src = e.target.result;
		};
		reader.readAsDataURL(file);
	  }
	});
  }});

