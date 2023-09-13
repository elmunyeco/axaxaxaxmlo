$(document).ready(function() {

	/***********************************************************************/
	/* PACIENTES */
	/***********************************************************************/
	$("#formAddPaciente").submit(function(){

		var action   = $(this).attr('action');
		var editando = false;
		var id 		 = $('#id').val();

		$('.boxloading').show();
		$('.msjError, #formAddPaciente, .msjPaciente, .btnVolver').hide();
		
		if($('#id').length > 0){
			action += "/" + id;
			editando = true;
		}

		$.ajax({
			   
		    type: "POST",
		    url: action,
		    data: $(this).serialize(),
		    dataType: "json",
		    success: function(data) {
			   	
				if(data.exito) {
				
					if(editando){					
						data = id;
						$('.msjPaciente').html("El paciente se ha actualizado correctamente.").show();
					} else {
						$('.msjPaciente').html("El nuevo paciente tiene asignada la historia clÃ­nica NÂ° " + data.num).show();
						data = data.num;
					}

					var strAncla=$('.header');

			Â Â Â Â Â Â Â Â //utilizamos body y html, ya que dependiendo del navegador uno u otro no funciona
			Â Â Â Â Â Â Â Â $('body,html').stop(true,true).animate({
			Â Â Â Â Â Â Â Â Â Â Â Â //realizamos la animacion hacia el ancla
			Â Â Â Â Â Â Â Â Â Â Â Â scrollTop: $(strAncla).offset().top
			Â Â Â Â Â Â Â Â },100);

					$('.btnOpcs').show();
					$('#refHC').attr('href', $('#refHC').attr('href') + "/" + data);

					$("#formAddPaciente").each(function(){
						this.reset();
					});
				  
				} else {
					
					if(data.msj)
						$('.msjError').html(data.msj).show();
					else							
						$('.msjError').show();
					$('.btnVolver').show();
				}

				$('.boxloading').hide();				
		    },
		    error: function(){
		    	$('.msjError').show();
		    	$('.boxloading').hide();
				$('#formAddPaciente').show();
		    }
		});

		return false;
	});

	// Agrego otro paciente en el formulario
	$('.btnNewPaciente').click(function(){
		$('.msjPaciente, .btnOpcs').hide();
		$('#formAddPaciente').show();
	});

	$('.eliminarPaciente').click(function(){

		if(confirm("Â¿Seguro que desea eliminar el paciente seleccionado?")){
			var id = $(this).attr('id');

			$.ajax({
				   
			    type: "POST",
			    url: $(this).attr('href'),
			    data: {id: id},
			    success: function(data) {
				   	
					if(data) {
						$('.fila_' + id ).remove();
					} else{
						$('#msjError').show();
					}
			    },
			    error: function(){
			    	$('#msjError').show();
			    }
			});
		}

		return false;
	});

	$('#formBuscador').submit(function(){

		if ( $('#campoBuscador').val() != ""){

			$.ajax({
				   
			    type: "POST",
			    url: $('#formBuscador').attr('action'),
			    data: $('#formBuscador').serialize(),
			    success: function(data) {
				   	
					if(data != 0) {
						
						$('.msjBuscador').html("").hide();
						$('.tBody').html(data);
						$('.boxFilter').show();
						$('#paginador').remove();

						$("#formBuscador").each(function(){
							this.reset();
						});
					  
					} else{
						$('.msjBuscador').html("No hay resultados para la busqueda realizada.").show();
						$('.boxFilter').hide();
					}
			    }
			});
		}
		
		return false;
	});

	// Buscador de pacientes
	$('#btnBuscador').click(function(){

		$('#formBuscador').trigger('submit');
		return false;
	});

	if( $('#fechaNac').val() ){
		
		var edad = calcular_edad($('#fechaNac').val());
		$('#edad').html("El paciente tiene " + edad + " aÃ±os.");
	}
	
	$('#fechaNac').change(function()
	{

		if($('#fechaNac').val() != "0000-00-00" && $('#fechaNac').val() != "")
		{
			var edad = calcular_edad($('#fechaNac').val());
			$('#edad').html("El paciente tiene " + edad + " aÃ±os.");
		} else {
			$('#edad').html("");
		}

	});

	$('.numberClass').keydown(function (e) {
		        
        // Allow: backspace, delete, tab, escape, enter and .
        if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) !== -1){
            
            return;

        }

        // Ensure that it is a number and stop the keypress
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });

	$('#fechaNac').keypress(function(event){

		if($(this).val().length == 2)
			$(this).val($(this).val() + '/');

		if($(this).val().length == 5)
			$(this).val($(this).val() + '/');
	});



	/***********************************************************************/
	/* HISTORIA CLINICA */
	/***********************************************************************/
	$('.copiarIndicacion').click(function(){
		
		$('.copiarIndicacion').hide();
		$('#panelLoading').show().css('display', 'block');

		$.ajax({
				   
		    type: "POST",
		    url: $(this).attr('href'),
		    success: function(data) {
			   	
			   	// Al copiar la indicaciÃ³n debo seleccionar el checkbox "Indicaciones" como Tipo de Comentario
				$("[name='tipoComentario']").each( function() { 

			        if ( $(this).val() == 2 )
			            $(this).attr('checked', true);

				});

				$('#comentarioIndicacion').html(data);
				$('#panelLoading').hide();

		    }
		});

		return false;
	});

	$('#formDiagnostico').submit(function(){

		$('.guardarComentario').hide();
		$('#enfLoading').addClass('glyphicon-refresh-animate');

		$.ajax({
				   
		    type: "POST",
		    url: $(this).attr('action'),
		    data: $(this).serialize(),
		    success: function(data) {
			   	
				$('.guardarComentario').show();
				$('#enfLoading').removeClass('glyphicon-refresh-animate');
		    }
		});

		return false;
	});

	$('.chEnfermedades').change(function(){

		$('#formDiagnostico').submit();
	});

	$('.enviarMail').click(function(){
				
		$('.cajaCorreo').fadeIn();
		$('.msjMail').hide();

		$("#formInforme").each(function(){
			this.reset();
		});

		return false;
	});
	
	$('#formInforme').submit(function(){
		
		$('#sendInforme').hide();
		$('#sendLoading').show().css('display', 'block');

		$.ajax({
				   
		    type: "POST",
		    url: $(this).attr('action'),
		    data: $(this).serialize(),
		    success: function(data) {
			   	
			   	if (data == 1){

			   		$('.msjMail').addClass('alert-success').html("Mail enviado exitosamente").show();

			   	} else {

			   		$('.msjMail').addClass('alert-danger').html("Error al enviar el mail").show();

			   	}	

				$('#sendInforme').show();
				$('#sendLoading').hide();
		    }
		});

		return false;
	});

	$('#closeSendResult').click(function(){

		$('.cajaCorreo').fadeOut();
		$('#sendInforme').show();
		$('#sendLoading').hide();
		
	});

	$('.divComentario').hover(function(){		

		$(this).find('a').show();

	} , function() {

		$(this).find('a').hide();

	});

	$('.eliminarComentario').click(function(){

		$(this).hide();
		$(this).parent().find('span').css('display', 'inline');

		var id = $(this).attr('id');
		
		$.ajax({
				   
		    type: "POST",
		    url: $(this).attr('href'),
		    success: function(data) {
		    	
		        $('#comentario_' + id ).remove();

		    }
		});

		return false;
	});


	// Accordion para los comentarios de la historia clinica
	$('.collapsed').click(function(){
		
		if($(this).prev().hasClass('glyphicon-chevron-down'))
			
			$(this).prev().removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-right');

		else{

			$('[data-toggle="collapse"]').each(function(index, item){
				$(this).prev().removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-right');
			});

			$(this).prev().removeClass('glyphicon-chevron-right').addClass('glyphicon-chevron-down');

		}

		var top = $(this).offset().top;
		$('html, body').animate({scrollTop: top},1000);
		var nodo = $(this).attr('href');

	});

	$('.btnGuardarDatos').click(function(){

		$('.formComentario').each(function(index, item){

			var form = $(this);
			var loading = form.prev();

			$(loading).show();
			form.hide();

			$.ajax({
					   
			    type: "POST",
			    async:false,
			    url: form.attr('action'),
			    data: form.serialize(),
			    success: function(data) {
				   	
					if(data) {
						
						form.each(function(){
							this.reset();
						});
					  
					}

					$(loading).hide();
					form.show();

			    },
			    error: function(){
			    	$(loading).hide();
					form.show();	
			    }
			});
	
		});	

		location.reload();
		return false;
	});

	$('.input').change(function(){
		$(this).val($(this).val().replace(',', '.'));
	});

	
	
	/***********************************************************************/
	/* INDICACIONES */
	/***********************************************************************/
	$("#formAddIndicacion").submit(function(){
		var action   = $(this).attr('action');
		var editando = false;
		var id 		 = $('#id').val();
		
		var textoError = "";
		
		if(document.getElementById("medicamento").value.trim()=="")
		{
			textoError = "Debe completar el medicamento.";
		}
		
		if(document.getElementById("ochoHoras").value.trim()=="" && document.getElementById("doceHoras").value.trim()=="" &&
		   document.getElementById("dieciochoHoras").value.trim()=="" && document.getElementById("veintiunaHoras").value.trim()=="")
		{
			if(textoError != "")
			{
				textoError += "<BR/>";
			}
			
			textoError += "Al menos un dato entre las 08:00, 12:00, 18:00 y 21:00 horas debe estar completo.";
		}
		
		if(textoError != "")
		{
			$('.msjError').html(textoError).show();
			return false;
		}

		$('.boxloading').show();
		$('.msjError, #formAddIndicacion, .msjIndicacion, .btnVolver').hide();
		
		if($('#id').length > 0){
			action += "/" + id;
			editando = true;
		}
		
		$.ajax({
		    type: "POST",
		    url: action,
		    data: $(this).serialize(),
		    dataType: "json",
		    success: function(data) {
				if(data.exito) {
					if(editando){					
						data = id;
						$('.msjIndicacion').html("La indicaciÃ³n se ha actualizado correctamente.").show();
					} else {
						$('.msjIndicacion').html("La nueva indicaciÃ³n se ha creado correctamente.").show();
					}

					var strAncla=$('.header');

			Â Â Â Â Â Â Â Â //utilizamos body y html, ya que dependiendo del navegador uno u otro no funciona
			Â Â Â Â Â Â Â Â $('body,html').stop(true,true).animate({
			Â Â Â Â Â Â Â Â Â Â Â Â //realizamos la animacion hacia el ancla
			Â Â Â Â Â Â Â Â Â Â Â Â scrollTop: $(strAncla).offset().top
			Â Â Â Â Â Â Â Â },100);

					$('.btnOpcs').show();
					$('#refHC').attr('href', $('#refHC').attr('href') + "/" + data);

					$("#formAddIndicacion").each(function(){
						this.reset();
					});
				} else {
					if(data.msj)
						$('.msjError').html(data.msj).show();
					else
						$('.msjError').show();
					$('#formAddIndicacion').show();
				}

				$('.boxloading').hide();				
		    },
		    error: function(){
		    	$('.msjError').show();
		    	$('.boxloading').hide();
				$('#formAddIndicacion').show();
		    }
		});

		return false;
	});

	// Agrego otra indicaciÃ³n en el formulario
	$('.btnNewIndicacion').click(function(){
		$('.msjIndicacion, .btnOpcs').hide();
		$('#formAddIndicacion').show();
	});

	$('.eliminarIndicacion').click(function(){
		var pagina1 = location.href
		//si la pÃ¡gina tiene 8 barras "/" -> tiene el nÃºmero del paginador -> entonces se lo saco para obtener la primera pÃ¡gina
		if(location.href.split("/").length-1 == 8)
		{
			var pagina1 = location.href.substring(0, location.href.lastIndexOf('/') + 1);
		}
		
		if(confirm("Â¿Seguro que desea eliminar la indicaciÃ³n seleccionada?")){
			var id = $(this).attr('id');
			$.ajax({
			    type: "POST",
			    url: $(this).attr('href'),
			    data: {id: id},
				dataType: "json",
			    success: function(data) {
					if(data.exito) {
						//si la tabla tiene 10 o menos objetos el paginador tiene que desaparecer, recargo la primera pÃ¡gina
						if(data.redirigirPagina1)
							// $('.msjError').html("-"+pagina1+"-").show();
							location.href = pagina1;
						else
							location.href  = location.href;
					} else{
						$('.msjError').html("Ha ocurrido un error al eliminar la indicaciÃ³n, intÃ©ntelo nuevamente").show();
					}
			    },
			    error: function(){
			    	$('.msjError').show();
			    }
			});
		}

		return false;
	});
	
	$('.guardarComentarioIndicacion').click(function(){		
		var comentario = $('#comentario').val();
		if(comentario.trim() == "")
		{
			$('.msjError').html("Debe completar el comentario").show();
			return false;
		}
		
		var idHC = $('#idHC').val();
		var proteger = $('.comentarioCheckbox:checked').val();
		if (proteger == undefined)
		{
			proteger = 0;
		}
		
		$('.msjError, .msjIndicacion').hide();
		
		$.ajax({
			type: "POST",
			url: $(this).attr('href'),
			data: {idHC: idHC, comentario: comentario, proteger: proteger, eliminado : 0},
			dataType: "json",
			success: function(data) {
				if(data.exito) {
					$('.msjIndicacion').html(data.msj).show();
				} else{
					$('.msjError').html(data.msj).show();
				}
			},
			error: function(){
				$('.msjError').html("Se produjo un error al realizar el proceso. IntÃ©ntelo nuevamente mÃ¡s tarde.").show();
			}
		});

		return false;
	});
	
	$('.eliminarComentarioIndicacion').click(function(){
		if(confirm("Â¿Seguro que desea eliminar la indicaciÃ³n seleccionada?")){
			var comentario = $('#comentario').val();
			var idHC = $('#idHC').val();
			var proteger = $('.comentarioCheckbox:checked').val();
			if (proteger == undefined)
			{
				proteger = 0;
			}
		
			$('.msjError, .msjIndicacion').hide();
			
			$.ajax({
			type: "POST",
			url: $(this).attr('href'),
			data: {idHC: idHC, comentario: comentario, proteger: proteger, eliminado : 1},
			dataType: "json",
			success: function(data) {
				if(data.exito) {
					$('.msjIndicacion').html(data.msj).show();
					$('#comentario').val("");
				} else{
					$('.msjError').html(data.msj).show();
				}
			},
			error: function(){
				$('.msjError').html("Se produjo un error al realizar el proceso. IntÃ©ntelo nuevamente mÃ¡s tarde.").show();
			}
		});
		}

		return false;
	});
	
	$('.cambiaComentario').keypress(function(e){
		$('.msjIndicacion').hide();
	});
	
	
	
	/***********************************************************************/
	/* SOLICITUDES */
	/***********************************************************************/
	$('.imprimirSolicitud').click(function(){
		$('.msjError, .msjIndicacion').hide();
		
		if($(":checkbox:checked").length == 0 && $('#otrasSolicitudes').val().trim() == "")
		{
			$('.msjError').html("Debe seleccionar al menos una solicitud.").show();
			return false;
		}
		
		var idHC = $('#idHC').val();
		var diagnostico = "-";
		if($('#diagnostico').val())
		{
			var diagnostico = $('#diagnostico').val();
			
			diagnostico = diagnostico.replaceAll("\n","|");
			diagnostico = diagnostico.replace(/\\/g, '|?1');
			diagnostico = diagnostico.replace(/\//g, '|?2');
			diagnostico = diagnostico.replace(/\'/g, '|?3');
			diagnostico = diagnostico.replace(/\*/g, '|?4');
			diagnostico = diagnostico.replace(/\!/g, '|?5');
			diagnostico = encodeURIComponent(diagnostico);
		}
		
		var url = $(this).attr('href');
		
		var solicitudes = new Array();
		
		$("input[type=checkbox]:checked").each(function(){
			var indice = 0;
			var auxiliar = "";
			var valor = $(this).attr("id");
			
			while(indice < solicitudes.length)
			{
				if(solicitudes[indice] > valor)
				{
					auxiliar = solicitudes[indice];
					solicitudes[indice] = valor;
					valor = auxiliar;
				}
				
				indice++;
			}
			
			if(indice == solicitudes.length)
			{
				solicitudes[indice] = valor;
			}
		});
		
		var solicitudesConjuntas = "";
		
		for(var i = 0; i < solicitudes.length; i++)
		{
			if(solicitudes[i].substring(2, 1) == 0)
			{
				solicitudesConjuntas += solicitudes[i] + "|";
				
				if(solicitudes.length <= i + 1 || solicitudes[i + 1].substring(2, 1) != 0)
				{
					solicitudesConjuntas = solicitudesConjuntas.substring(0, solicitudesConjuntas.length - 1);
					window.open(url + "/" + idHC + "/" + diagnostico + "/" + solicitudesConjuntas);
				}
			}
			else
			{
				window.open(url + "/" + idHC + "/" + diagnostico + "/" + solicitudes[i]);
			}
		}
		
		if($('#otrasSolicitudes').val().trim() != "")
		{
			var otrasSolicitudesArray = new Array();
			
			otrasSolicitudesArray = $('#otrasSolicitudes').val().trim().split("\n");
			
			for(var i = 0; i < otrasSolicitudesArray.length; i++)
			{
				otrasSolicitudesArray[i] = otrasSolicitudesArray[i].replace(/\\/g, '|?1');
				otrasSolicitudesArray[i] = otrasSolicitudesArray[i].replace(/\//g, '|?2');
				otrasSolicitudesArray[i] = otrasSolicitudesArray[i].replace(/\'/g, '|?3');
				otrasSolicitudesArray[i] = otrasSolicitudesArray[i].replace(/\*/g, '|?4');
				otrasSolicitudesArray[i] = otrasSolicitudesArray[i].replace(/\!/g, '|?5');
				otrasSolicitudesArray[i] = encodeURIComponent(otrasSolicitudesArray[i]);
				
				window.open(url + "/" + idHC + "/" + diagnostico + "/" + otrasSolicitudesArray[i] + "/1");
			}
		}
		
		// window.open(url + "/" + idHC + "/" + diagnostico + "/" + $(this).attr("id"));
		// $('.msjError').html(url + "?idHC=" + idHC + "&diagnostico=" + diagnostico + "&solicitud=" + $(this).attr("id")).show();
		
		// $('.msjError').html("1- " +  solicitudesConjuntas /*+ "ind:" + indice*/).show();

		return false;
	});
	
	String.prototype.replaceAll = function(search, replacement) {
		var target = this;
		return target.replace(new RegExp(search, 'g'), replacement);
	};
	
	
	
	
	
	/***********************************************************************/
	/* USUARIOS */
	/***********************************************************************/
	$('#formUsuario').submit(function(){

		if($('#pass').val() == $('#repitePass').val())
		{
			$('#msjUsuario').html("").removeClass("alert-success").removeClass("alert-danger").hide();
			$('.boxloading').show();
			$(this).hide();

			$.ajax({
				   
			    type: "POST",
			    url: $('#formUsuario').attr('action'),
			    data: $('#formUsuario').serialize(),
			    dataType: "json",
			    success: function(data) {
				   	
					if(data.exito) {
						
						$("#formUsuario").each(function(){
							this.reset();
						});

						$('#msjUsuario').html("Los datos se han actualizado correctamente.").addClass('alert-success').show();
						$('#usuario').val(data.usuario);
					  
					} else{	
						$('#msjUsuario').html("Se ha producido un error al actualizar los datos. IntÃ©ntelo mÃ¡s tarde.").addClass('alert-danger').show();
					}

					$('.boxloading').hide();
					$('#formUsuario').show();
			    },
			    error: function(){
			    	$('#msjUsuario').html("Se ha producido un error al actualizar los datos. IntÃ©ntelo mÃ¡s tarde.").addClass('alert-danger').show();
			    	$('.boxloading').hide();
					$('#formUsuario').show();
			    }
			});	
		} else {
			$('#msjUsuario').html("Las contraseÃ±as ingresadas no son iguales. IntÃ©ntelo nuevamente.").addClass('alert-danger').show();
		}

		return false;
	});



	/***********************************************************************/
	/* ESTUDIOS */
	/***********************************************************************/
	// Buscador de estudios
	$('#btnEstudios').click(function(){
		
		if(validarFechas()){

			$('#btnEstudios').attr('disabled', 'disabeld');
			$('#spnBuscar').html('Buscando...');
			$('#ldgBuscar').css('display', 'inline-block');
			$('#iconBuscar').hide();

			$.ajax({
				   
			    type: "POST",
			    url: $('#formEstudios').attr('action'),
			    data: $('#formEstudios').serialize(),
			    dataType: "json",
			    success: function(data) {
				   	
					if( !jQuery.isEmptyObject(data.estudios) ) {
						
						$('.msjBuscador').html("").hide();
						$('.tBody').html(data);
						$('.boxFilter').show();
						$('#paginador').remove();

						$(data).each(function(index, item){

							$('.tBody').append(data.estudios);
						});

					} else{
						$('.msjBuscador').html("No hay resultados para la bÃºsqueda realizada.").show();
						$('.boxFilter').hide();
					}

					$('#ldgBuscar').hide();
					$('#spnBuscar').html('Buscar').show();
					$('#btnEstudios').removeAttr('disabled');
					$('#iconBuscar').show();
			    },
			    error: function(){
			    	$('#ldgBuscar').hide();
					$('#spnBuscar').html('Buscar').show();
					$('#btnEstudios').removeAttr('disabled');
					$('#iconBuscar').show();
			    }
			});
		}
		
		return false;

	});

	$('.mailIcon').click(function(){
		
		$(this).next().show();
		$(this).hide();
		return false;
	});

	$('.btnCancelar').click(function(){
		$(this).parent().parent().hide();
		$(this).parent().parent().prev().show();
	});

	$('.sendMail').submit(function(){

		var nodo = $( this );
		$( nodo ).find('.btnSend').attr('disabled', 'disabeld');
		$( nodo ).find('.spnSend').html('Enviando...');
		$( nodo ).find('.ldgSend').css('display', 'inline-block');
		
		$.ajax({
			   
		    type: "POST",
		    url: $( nodo ).attr('action'),
		    data: $( nodo ).serialize(),
		    success: function(data) {
				$( nodo ).find('.ldgSend').css('display', 'none');
				$( nodo ).find('.spnSend').html('Enviar').show();
				$( nodo ).find('.btnSend').removeAttr('disabled');
				$( nodo ).find('.mail').val('');
				$( nodo ).find('.btnCancelar').trigger('click');
		    },
		    error: function(){
		    	$( nodo ).find('.ldgSend').css('display', 'none');
				$( nodo ).find('.spnSend').html('Enviar').show();
				$( nodo ).find('.btnSend').removeAttr('disabled');
		    }
		});

		return false;
	});

	// Footer
	var height = $('body').height();
	var hWindow = $(window).height();
	
	if( height < hWindow)
		$('.footer').addClass('bottom');

	// Seteo el alto del menÃº hasta el final de la pÃ¡gina
	$('.mainContainer .menu').height(height);
});

/*************************************************************************/
/*     FUNCIONES 				 										 */
/*************************************************************************/		
function validarFormulario(){
	var tipoDoc		= $('#tipoDoc'),
		numDoc 		= $('#numDoc'),
		nombre	 	= $('#nombre'),
		apellido 	= $('#apellido'),		
		mail 		= $('#mail'),
		direccion 	= $('#direccion');

	if($.trim(tipoDoc.val()) == '' || tipoDoc.val() == null){
		$('.msjRegistrar').html('El campo tipo de documento es obligatorio');
		$(tipoDoc).focus();
		return false;
	}
	if($.trim(numDoc.val()) == '' || numDoc.val() == null){
		$('.msjRegistrar').html('El campo nÃºmero de documento es obligatorio');
		$(numDoc).focus();
		return false;
	}
	if($.trim(nombre.val()) == '' || nombre.val() == null){
		$('.msjRegistrar').html('El campo NOMBRE es obligatorio');
		$(nombre).focus();
		return false;
	}
	if($.trim(apellido.val()) == '' || apellido.val() == null){
		$('.msjRegistrar').html('El campo APELLIDO es obligatorio');
		$(apellido).focus();
		return false;
	}
	
	if($.trim(mail.val()) == '' || mail.val() == null){
		$('.msjRegistrar').html('El campo MAIL es obligatorio');
		$(mail).focus();
		return false;
	}else{
		//Verifico si lo ingresado cumple con la expresiÃ³n regular del formato que tiene un correo electrÃ³nico
		expr_reg = /^[a-zA-Z0-9\._-]+@[a-zA-Z0-9-]{2,}[.][a-zA-Z]{2,4}$/;
		if(!mail.val().match(expr_reg)) {  
		    $('.msjRegistrar').html("Ingrese una direcciÃ³n de correo vÃ¡lida");
		    $(mail).focus();
			return false;
		}
	}
	if($.trim(direccion.val()) == '' || direccion.val() == null){
		$('.msjRegistrar').html('El campo direcciÃ³n es obligatorio');
		$(direccion).focus();
		return false;
	}

	$('.msjRegistrar').html('');
	return true;
}

function calcular_edad(fecha) {

	var fechaActual = new Date()
	var diaActual = fechaActual.getDate();
	var mmActual = fechaActual.getMonth() + 1;
	var yyyyActual = fechaActual.getFullYear();
	FechaNac = fecha.split("/");
	var diaCumple = FechaNac[0];
	var mmCumple = FechaNac[1];
	var yyyyCumple = FechaNac[2];
	
	//retiramos el primer cero de la izquierda
	if (mmCumple.substr(0,1) == 0) 
	{
		mmCumple= mmCumple.substring(1, 2);
	}

	//retiramos el primer cero de la izquierda
	if (diaCumple.substr(0, 1) == 0) 
	{
		diaCumple = diaCumple.substring(1, 2);
	}
	
	var edad = yyyyActual - yyyyCumple;

	//validamos si el mes de cumpleaÃ±os es menor al actual
	//o si el mes de cumpleaÃ±os es igual al actual
	//y el dia actual es menor al del nacimiento
	//De ser asi, se resta un aÃ±o
	if ((mmActual < mmCumple) || (mmActual == mmCumple && diaActual < diaCumple)) 
	{
		edad--;
	}

	return edad;
};

function validarFechas()
{
	var fechaDesde = $('#fechaDesde').val();
	var fechaHasta = $('#fechaHasta').val();

	if( $.trim(fechaDesde) == "" || fechaDesde == null ) {
		$('#fechaDesde').parent().addClass('has-error');
		$('#fechaDesde').parent().find('.form-control-feedback').show();
		return false;
	} else {
		
		$('#fechaDesde').parent().removeClass('has-error');
		$('#fechaDesde').parent().find('.form-control-feedback').hide();

		if( $.trim(fechaHasta) == "" || fechaHasta == null ) {
			$('#fechaHasta').parent().addClass('has-error');
			$('#fechaHasta').parent().find('.form-control-feedback').show();
			return false;
		}
		$('#fechaHasta').parent().find('.form-control-feedback').hide();
		$('#fechaHasta').parent().removeClass('has-error');
	}

	return true;
}
