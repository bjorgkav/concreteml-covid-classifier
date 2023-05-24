from django.shortcuts import render, HttpResponse, HttpResponseRedirect

# Create your views here.
def hello_world(request):
    return render(request, 'index.html')

def show_input(request):
    if request.method == 'POST':
        # form = ContactForm(request.POST) #not gonna use it since we're not gonna make a model
        # form_input = dict(request.POST.lists())
        form_input = {key:value for key, value in request.POST.items()}
        file_input = {key:value for key, value in request.FILES.items()}
        
        print(form_input)

        #for key, value in form_input.items():
        #    print(f"{key}: {value}")
        
        return render(request, 'show_input.html', {'form_input':form_input, 'file_input':file_input})
    

    
def client_generate_keys(request):
    pass