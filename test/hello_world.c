#include <stdio.h>

void
print_initial_scripts ()
{
	printf("This program is for testing GitHub Action and Git diff.\n") ;
	printf("I want to find out what function is changed using git diff.\n") ;
	printf("If the commit change is arise, Git Action will detect it.\n") ;
}

int
main ()
{
	printf("Hello, world!\n") ;
	print_initial_scripts() ;

	return 0 ;
}
