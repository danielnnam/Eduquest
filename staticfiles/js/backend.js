// Edit content file code 
document.getElementById('content_type').addEventListener('change', function() {
    var selectedType = this.value;
    document.getElementById('text_content').style.display = selectedType === 'text' ? 'block' : 'none';
    document.getElementById('video_content').style.display = selectedType === 'video' ? 'block' : 'none';
    document.getElementById('document_content').style.display = selectedType === 'document' ? 'block' : 'none';
});


// Instructors base code 

// progress form
$(document).ready(function() {
    let currentStep = 1;

    // Move to the next step
    $('.nextBtn').on('click', function() {
        console.log("Next button clicked!");
        if ($("#courseForm")[0].checkValidity()) {
            $(`#step${currentStep}`).hide();
            currentStep++;
            $(`#step${currentStep}`).show();
            updateProgressBar();
        } else {
            $("#courseForm")[0].reportValidity();
        }
    });

    // Move to the previous step
    $('.prevBtn').on('click', function() {
        $(`#step${currentStep}`).hide();
        currentStep--;
        $(`#step${currentStep}`).show();
        updateProgressBar();
    });

    // Update progress bar
    function updateProgressBar() {
        let progress = (currentStep / 2) * 100;
        $('#progressBar').css('width', `${progress}%`);
        $('#progressBar').text(`Step ${currentStep} of 2`);
    }

   
});

$(document).ready(function() {
  $('#quizTable').DataTable({
    "paging": true,        // Enable pagination
    "searching": true,     // Enable search filter
    "ordering": true,      // Enable sorting
    "info": true           // Show information like "Showing X of Y entries"
  });
});