% BibTeX bibliography style `ams.bst' without sorting
% Style of American Math. Soc. without sorting
        % version 0.99a for BibTeX versions 0.99a or later, LaTeX version 2.09.
        % The file btxbst.doc has some documentation for this style.
% Written by Steven Duplij:
% Kharkov State University, Ukraine and Kaiserslautern University, Germany
% E-mail: duplij@physik.uni-kl.de
% WWW: http://www.math.uni-mannheim.de/~duplij/
% Comments and improvements are welcome
% Tels.: +38-0572-219818 (Kharkov) and +49-631-43278 (Kaiserslautern)

ENTRY
  { address
    author
    booktitle
    chapter
    edition
    editor
    howpublished
    institution
    journal
    key
    month
    note
    number
    organization
    pages
    publisher
    school
    series
    title
    type
    volume
    year
  }
  { multi.ref }
  { label }

INTEGERS { output.state before.all mid.sentence after.sentence after.block }
INTEGERS { mid.block }
STRINGS { previous.author previous.journal }

FUNCTION {init.state.consts}
{ #0 'before.all :=
  #1 'mid.sentence :=
  #2 'after.sentence :=
  #3 'after.block :=
  #4 'mid.block :=
}

STRINGS { s t }

FUNCTION {output.nonnull}
{ 's :=
  output.state mid.sentence =
    { ", " * write$ }
    { output.state after.block =
        { write$
          newline$
          "\newblock " write$
        }
        { output.state before.all =
            'write$
            { output.state mid.block =
               { "," * write$ newline$ "\newblock " write$ }
               { " " * write$ }
             if$
            }
          if$
        }
      if$
      mid.sentence 'output.state :=
    }
  if$
  s
}

FUNCTION {output}
{ duplicate$ empty$
    'pop$
    'output.nonnull
  if$
}

FUNCTION {output.check}
{ 't :=
  duplicate$ empty$
    { pop$ "empty " t * " in " * cite$ * warning$ }
    'output.nonnull
  if$
}

FUNCTION {output.bibitem}
{ multi.ref
  { ""
    before.all 'output.state :=
  }
  { newline$
    "\bibitem{" write$
    cite$ write$
    "}" write$
    newline$
    ""
    before.all 'output.state :=
  }
 if$
}

FUNCTION {fin.entry}
{ multi.ref #1 >
  { "; " * write$
    newline$
    "\newblock " write$
    before.all 'output.state :=
  }
  { add.period$
    write$
    newline$
  }
 if$
 multi.ref #1 =
 { "" "" }
 { author missing$
      { "" }
      { author }
    if$
    journal missing$
      { "" }
      { journal }
    if$
 }
 if$
 'previous.journal :=
 'previous.author :=
 }

FUNCTION {new.block}
{ output.state before.all =
    'skip$
    { after.block 'output.state := }
  if$
}

FUNCTION {new.sentence}
{ output.state after.block =
    'skip$
    { output.state before.all =
        'skip$
        { after.sentence 'output.state := }
      if$
    }
  if$
}

FUNCTION {btw.block}
{ output.state before.all =
    'skip$
    { mid.block 'output.state := }
  if$
}

FUNCTION {not}
{   { #0 }
    { #1 }
  if$
}

FUNCTION {and}
{   'skip$
    { pop$ #0 }
  if$
}

FUNCTION {or}
{   { pop$ #1 }
    'skip$
  if$
}

FUNCTION {new.block.checka}
{ empty$
    'skip$
    'new.block
  if$
}

FUNCTION {new.block.checkb}
{ empty$
  swap$ empty$
  and
    'skip$
    'new.block
  if$
}

FUNCTION {new.sentence.checka}
{ empty$
    'skip$
    'new.sentence
  if$
}

FUNCTION {new.sentence.checkb}
{ empty$
  swap$ empty$
  and
    'skip$
    'new.sentence
  if$
}

FUNCTION {field.or.null}
{ duplicate$ empty$
    { pop$ "" }
    'skip$
  if$
}

FUNCTION {emphtt}
{ duplicate$ empty$
    { pop$ "" }
    { "{\tt " swap$ * "}" * }
  if$
}

FUNCTION {emphsl}
{ duplicate$ empty$
    { pop$ "" }
    { "{\sl " swap$ * "}" * }
  if$
}

FUNCTION {emphserif}
{ duplicate$ empty$
    { pop$ "" }
    { "{\sf " swap$ * "}" * }
  if$
}

FUNCTION {emphasize}
{ duplicate$ empty$
    { pop$ "" }
    { "{\it " swap$ * "}" * }
  if$
}

FUNCTION {emphbold}
{ duplicate$ empty$
    { pop$ "" }
    { "{\bf " swap$ * "}" * }
  if$
}

FUNCTION {bracket}
{ "(" swap$ ")" * *
}

INTEGERS { nameptr namesleft numnames }

FUNCTION {format.names}
{ 's :=
  #1 'nameptr :=
  s num.names$ 'numnames :=
  numnames 'namesleft :=
    { namesleft #0 > }
    { s nameptr "{f. }{vv~}{ll}{, jj}" format.name$ 't :=
      nameptr #1 >
        { namesleft #1 >
            { ", " * t * }
            { numnames #2 >
                { "," * }
                'skip$
              if$
              t "others" =
                { " et~al." * }
                { " and " * t * }
              if$
            }
          if$
        }
        't
      if$
      nameptr #1 + 'nameptr :=
      namesleft #1 - 'namesleft :=
    }
  while$
}

FUNCTION {format.authors}
{ author empty$
    { "" }
    { author previous.author =
        { multi.ref
          { "" }
          { "---------" }
          if$
         }
         { author format.names }
      if$
    }
  if$
}

FUNCTION {format.editors}
{ editor empty$
    { "" }
    { editor format.names
      editor num.names$ #1 >
       { ", eds." * }
       { ", ed." * }
      if$
      bracket
    }
  if$
}

FUNCTION {format.title}
{ title empty$
    { "" }
    { title "t" change.case$ emphasize }
  if$
}

FUNCTION {n.dashify}
{ 't :=
  ""
    { t empty$ not }
    { t #1 #1 substring$ "-" =
        { t #1 #2 substring$ "--" = not
            { "--" *
              t #2 global.max$ substring$ 't :=
            }
            {   { t #1 #1 substring$ "-" = }
                { "-" *
                  t #2 global.max$ substring$ 't :=
                }
              while$
            }
          if$
        }
        { t #1 #1 substring$ *
          t #2 global.max$ substring$ 't :=
        }
      if$
    }
  while$
}

FUNCTION {format.date}
{ year empty$
    { month empty$
        { "" }
        { "there's a month but no year in " cite$ * warning$
          month
        }
      if$
    }
    { month empty$
        'year
        { month " " * year * }
      if$
    }
  if$
}

FUNCTION {format.btitle}
{ title emphasize
}

FUNCTION {tie.or.space.connect}
{ duplicate$ text.length$ #3 <
    { "~" }
    { " " }
  if$
  swap$ * *
}

FUNCTION {either.or.check}
{ empty$
    'pop$
    { "can't use both " swap$ * " fields in " * cite$ * warning$ }
  if$
}

FUNCTION {format.bvolume}
{ volume empty$
    { "" }
    { "Vol." volume tie.or.space.connect
      series empty$
        'skip$
        { " of " * series emphasize * }
      if$
      "volume and number" number either.or.check
    }
  if$
}

FUNCTION {format.number.series}
{ volume empty$
    { number empty$
        { series field.or.null }
        { output.state mid.sentence =
            { "n." }
            { "Number" }
          if$
          number tie.or.space.connect
          series empty$
            { "there's a number but no series in " cite$ * warning$ }
            { " in " * series * }
          if$
        }
      if$
    }
    { "" }
  if$
}

FUNCTION {format.edition}
{ edition empty$
    { "" }
    { output.state mid.sentence =
        { edition "l" change.case$ " edition" * }
        { edition "t" change.case$ " edition" * }
      if$
    }
  if$
}

INTEGERS { multiresult }

FUNCTION {multi.page.check}
{ 't :=
  #0 'multiresult :=
    { multiresult not
      t empty$ not
      and
    }
    { t #1 #1 substring$
      duplicate$ "-" =
      swap$ duplicate$ "," =
      swap$ "+" =
      or or
        { #1 'multiresult := }
        { t #2 global.max$ substring$ 't := }
      if$
    }
  while$
  multiresult
}

FUNCTION {format.pages}
{ pages empty$
    { "" }
    { pages multi.page.check
        { "pp. " pages n.dashify tie.or.space.connect }
        { "p." pages tie.or.space.connect }
      if$
    }
  if$
}

FUNCTION {format.vol.num.pages}
{ " " volume * duplicate$ empty$
  { "Empty volume in " cite$ * warning$ pop$
  }
  { emphbold
    pages empty$
      { "Empty pages in " cite$ * warning$
      }
      { " " * year bracket * ", " *
        pages duplicate$ multi.page.check
          'n.dashify
          'skip$
        if$
        *
      }
    if$
  }
if$
}

FUNCTION {format.chapter.pages}
{ chapter empty$
    'format.pages
    { type empty$
        { "Chap." }
        { type "l" change.case$ }
      if$
      chapter tie.or.space.connect
      pages empty$
        'skip$
        { ", " * format.pages * }
      if$
    }
  if$
}

FUNCTION {format.in.ed.booktitle}
{ booktitle empty$
    { "" }
    { editor empty$
    { "in " booktitle * }
    { "in " booktitle * ",  " * format.editors * }
      if$
    }
  if$
}

FUNCTION {empty.misc.check}
{ author empty$ title empty$ howpublished empty$
  month empty$ year empty$ note empty$
  and and and and and
    { "all relevant fields are empty in " cite$ * warning$ }
    'skip$
  if$
}

FUNCTION {format.thesis.type}
{ type empty$
    'skip$
    { pop$
      type "t" change.case$
    }
  if$
}

FUNCTION {format.tr.number}
{ type empty$
    { "Technical Report" }
    'type
  if$
  number empty$
    { "t" change.case$ }
    { number tie.or.space.connect }
  if$
}

FUNCTION {format.note}
{ note duplicate$ empty$
    { pop$ "" }
    { bracket }
  if$
}

FUNCTION {write.publ.addr.year}
{ publisher empty$
  { address empty$
    'btw.block
    { "(" address * output.nonnull }
  if$
  }
  { "(" publisher * output.nonnull
    address output
  }
 if$
 format.date
 address empty$ publisher empty$ and
   'skip$
   { ")" * }
 if$
 output
}


FUNCTION {format.article.crossref}
{ key empty$
    { journal empty$
        { "need key or journal for " cite$ * " to crossref " * crossref *
          warning$
          ""
        }
        { "In {\it " journal * "\/}" * }
      if$
    }
    { "In " key * }
  if$
  " \cite{" * crossref * "}" *
}

FUNCTION {format.crossref.editor}
{ editor #1 "{vv~}{ll}" format.name$
  editor num.names$ duplicate$
  #2 >
    { pop$ " et~al." * }
    { #2 <
        'skip$
        { editor #2 "{ff }{vv }{ll}{ jj}" format.name$ "others" =
            { " et~al." * }
            { " and " * editor #2 "{vv~}{ll}" format.name$ * }
          if$
        }
      if$
    }
  if$
}

FUNCTION {format.book.crossref}
{ volume empty$
    { "empty volume in " cite$ * "'s crossref of " * crossref * warning$
      "In "
    }
    { "Volume" volume tie.or.space.connect
      " of " *
    }
  if$
  editor empty$
  editor field.or.null author field.or.null =
  or
    { key empty$
        { series empty$
            { "need editor, key, or series for " cite$ * " to crossref " *
              crossref * warning$
              "" *
            }
            { "{\it " * series * "\/}" * }
          if$
        }
        { key * }
      if$
    }
    { format.crossref.editor * }
  if$
  " \cite{" * crossref * "}" *
}

FUNCTION {format.incoll.inproc.crossref}
{ editor empty$
  editor field.or.null author field.or.null =
  or
    { key empty$
        { booktitle empty$
            { "need editor, key, or booktitle for " cite$ * " to crossref " *
              crossref * warning$
              ""
            }
            { "In {\it " booktitle * "\/}" * }
          if$
        }
        { "In " key * }
      if$
    }
    { "In " format.crossref.editor * }
  if$
  " \cite{" * crossref * "}" *
}

FUNCTION {article}
{ output.bibitem
  format.authors "author" output.check
  btw.block
  format.title "title" output.check
  btw.block
  crossref missing$
    { journal "journal" output.check
      new.block
      format.vol.num.pages output
    }
    { format.article.crossref output.nonnull
      format.pages output
    }
  if$
  new.block
  format.note output
  fin.entry
}

FUNCTION {book}
{ output.bibitem
  author empty$
    { format.editors "author and editor" output.check }
    { format.authors output.nonnull
      crossref missing$
        { "author and editor" editor either.or.check }
        'skip$
      if$
    }
  if$
  btw.block
  format.btitle "title" output.check
  btw.block
  crossref missing$
    { format.bvolume output
      btw.block
      format.number.series output
      format.edition output
      btw.block
      publisher "publisher" output.check
      btw.block
      address output
    }
    { btw.block
      format.book.crossref output.nonnull
    }
  if$
  format.date "year" output.check
  new.block
  format.note output
  fin.entry
}


FUNCTION {booklet}
{ output.bibitem
  format.authors output
  new.block
  format.title "title" output.check
  howpublished address new.block.checkb
  howpublished output
  address output
  format.date output
  new.sentence
  format.note output
  fin.entry
}

FUNCTION {inbook}
{ output.bibitem
  author empty$
    { format.btitle "title" output.check
      btw.block
      format.editors "author and editor" output.check }
    { format.authors output.nonnull
      crossref missing$
       { "author and editor" editor either.or.check }
       'skip$
      if$
      btw.block
      format.btitle "title" output.check
    }
  if$
  btw.block
  crossref missing$
    { format.bvolume output
      format.edition output
      format.number.series output
      btw.block
      publisher "publisher" output.check
      address output
    }
    { format.chapter.pages "chapter and pages" output.check
      new.block
      format.book.crossref output.nonnull
    }
  if$
  format.date "year" output.check
  btw.block
  format.chapter.pages "chapter and pages" output.check
  new.block
  format.note output
  fin.entry
}

FUNCTION {incollection}
{ output.bibitem
  format.authors "author" output.check
  btw.block
  format.title "title" output.check
  btw.block
  crossref missing$
    { format.in.ed.booktitle "booktitle" output.check
      format.bvolume output
      format.number.series output
      btw.block
      publisher "publisher" output.check
      address output
      btw.block
      format.edition output
      format.date "year" output.check
    }
    { format.incoll.inproc.crossref output.nonnull
      format.chapter.pages output
    }
  if$
  btw.block
  format.chapter.pages output
  new.block
  format.note output
  fin.entry
}



FUNCTION {inproceedings}
{ output.bibitem
  format.authors "author" output.check
  btw.block
  format.title "title" output.check
  btw.block
   crossref missing$
    { format.in.ed.booktitle "booktitle" output.check
      format.bvolume output
      format.number.series output
      btw.block
      address empty$
       { organization publisher new.sentence.checkb
         organization output
         publisher output
         format.date "year" output.check
       }
       { organization output
         publisher output
         address output.nonnull
         format.date "year" output.check
       }
      if$
    }
    { format.incoll.inproc.crossref output.nonnull
      format.pages output
    }
  if$
  format.pages output
  new.block
  format.note output
  fin.entry
}



FUNCTION {conference} { inproceedings }

FUNCTION {manual}
{ output.bibitem
  author empty$
    { organization empty$
        'skip$
        { organization output.nonnull
          address output
        }
      if$
    }
    { format.authors output.nonnull }
  if$
  new.block
  format.btitle "title" output.check
  author empty$
    { organization empty$
        { address new.block.checka
          address output
        }
        'skip$
      if$
    }
    { organization output
      address output
    }
  if$
  format.edition output
  format.date output
  new.sentence
  format.note output
  fin.entry
}

FUNCTION {mastersthesis}
{ output.bibitem
  format.authors "author" output.check
  new.block
  format.title "title" output.check
  new.block
  "Master's thesis" format.thesis.type output.nonnull
  school "school" output.check
  address output
  format.date "year" output.check
  new.sentence
  format.note output
  fin.entry
}

FUNCTION {misc}
{ output.bibitem
  format.authors output
  title howpublished new.block.checkb
  format.title output
  howpublished new.block.checka
  howpublished output
  format.date output
  new.sentence
  format.note output
  fin.entry
  empty.misc.check
}

FUNCTION {mref}
{ title missing$
    { output.bibitem pop$ }
    { "Unknown 1st symbol in " cite$ * " ,the reference ignored" * warning$
    }
    if$
}

FUNCTION {phdthesis}
{ output.bibitem
  format.authors "author" output.check
  btw.block
  format.btitle "title" output.check
  btw.block
  "PhD thesis" format.thesis.type output.nonnull
  school "school" output.check
  address output
  format.date "year" output.check
  new.block
  format.note output
  fin.entry
}

FUNCTION {proceedings}
{ output.bibitem
  format.btitle "title" output.check
  btw.block
  editor empty$
    { organization output }
    { format.editors output.nonnull }
  if$
  btw.block
  format.bvolume output
  format.number.series output
  btw.block
  address empty$
    { editor empty$
        { publisher new.sentence.checka }
        { organization publisher new.sentence.checkb
          organization output
        }
      if$
      publisher output
    }
    { publisher output
      address output.nonnull
    }
  if$
  format.date "year" output.check
  new.block
  format.note output
  fin.entry
}



FUNCTION {techreport}
{ output.bibitem
  format.authors "author" output.check
  new.block
  format.title "title" output.check
  new.block
  format.tr.number output.nonnull
  institution "institution" output.check
  address output
  format.date "year" output.check
  new.sentence
  format.note output
  fin.entry
}

FUNCTION {unpublished}
{ output.bibitem
  before.all 'output.state :=
  format.authors "author" output.check
  format.title "" * "title" output.check
  publisher emphsl " {\it preprint}" *
  volume empty$
    'skip$
    {", " * volume *}
  if$
  number empty$
    'skip$
    {", " * number emphtt *}
  if$
  "" * "publisher" output.check
  " " address * "" * "address" output.check
  format.date add.period$ "date" output.check
  fin.entry
}


FUNCTION {default.type} { misc }


MACRO {ac}  {"Acta Cybernet"}
MACRO {aem} {"Aequationes Math."}
MACRO {afr} {"Acta Fac. Rerum. Natur. Univ. Commenian. Math. Publ."}
MACRO {ail}  {"Algebra i Logica"}
MACRO {am} {"Adv. Math."}
MACRO {amh} {"Acta Math. Hung."}
MACRO {amm} {"Amer. Math. Monthly"}
MACRO {amas} {"Acta Math. Acad. Sci. Hungar"}
MACRO {amb}  {"Arch. Math. (Basel)"}
MACRO {app} {"Acta Phys. Pol. "}
MACRO {ap} {"Ann. Phys."}
MACRO {asm}  {"Acta. Sci. Math."}
MACRO {au} {"Algebra Universalis"}
MACRO {aucmp} {"Acta Univ. Carolinae - Math. et Phys."}
MACRO {bams} {"Bull. Amer. Math. Soc."}
MACRO {baums} {"Bull. Austr. Math. Soc."}
MACRO {bap} {"Bull. Acad. Polon. Sci., Ser.: Math."}
MACRO {bsrs} {"Bull. Soc. Roy. Sci."}
MACRO {bsmm} {"Bol. Soc. Mat. Mexicana"}
MACRO {bsmpm} {"Bull. Soc. Math. Phys. Macedone"}
MACRO {btgu} {"Bull. Tokyo Gakugei Univ."}
MACRO {bumi} {"Boll. Univ. Mat. Ital."}
MACRO {ca} {"Commun. Algebra"}
MACRO {cjm} {"Can. J. Math."}
MACRO {cmj} {"Czech. Math. J."}
MACRO {cmp} {"Comm. Math. Phys."}
MACRO {cmb} {"Canad. Math. Bull."}
MACRO {cm}  {" Colloq. Math."}
MACRO {cmuc} {"Comment. Math. Univ. Carolina"}
MACRO {cnpp} {"Comment. Nucl. Part. Phys"}
MACRO {com}  {"Collect. Math."}
MACRO {coma} {"Compositio Math."}
MACRO {cpm} {"Casopis Pect. Mat."}
MACRO {cqg} {"Class. Q. Grav."}
MACRO {crabs} {"C. R. Acad. Bulgare Sci."}
MACRO {dm} {"Demonstr. Math."}
MACRO {dmj} {"Duke Math. J."}
MACRO {dsm}  {"Discrete Math."}
MACRO {fan} {"Func. Anal. Appl."}
MACRO {fm}  {"Fund. math."}
MACRO {fsu} {"Fac. Sci. Univ. Skopje Annuaire"}
MACRO {glm} {"Glasnik Mat."}
MACRO {gmj} {"Glasgow Math. J."}
MACRO {gm} {"Gas. Mat."}
MACRO {grg} {"Gen. Rel. Grav."}
MACRO {g} {"Ganita"}
MACRO {hjm} {"Houston J. Math."}
MACRO {ic}  {"Inform and Control"}
MACRO {ijpam} {"Indian J. Pure Appl. Math."}
MACRO {ijtp} {"Int. J. Theor. Phys."}
MACRO {ijmp} {"Int. J. Mod. Phys."}
MACRO {ja} {"J.~Algebra"}
MACRO {jaums} {"J.~Austr. Math. Soc."}
MACRO {jcss} {"J.~Comput. System. Sci."}
MACRO {jct} {"J.~Combinatorial Theory"}
MACRO {jgp} {"J.~Geom. and Phys."}
MACRO {jlms} {"J.~London Math. Soc."}
MACRO {jmp} {"J.~Math. Phys."}
MACRO {jnsm} {"J.~Natural Sci. and Math."}
MACRO {jp} {"J.~Phys."}
MACRO {jpm} {"J.~Pure Math."}
MACRO {jpaa} {"J.~Pure Appl. Algebra"}
MACRO {jram} {"J. Reine Angew. Math."}
MACRO {jrnbs} {"J. Res. Nat. Bur. Standards"}
MACRO {kjm} {"Kobe J. Math."}
MACRO {kmj} {"Kyungpook. Math. J."}
MACRO {lmp} {"Lett. Math. Phys."}
MACRO {lnp} {"Lect. Notes Phys."}
MACRO {lnm} {"Lect. Notes Math."}
MACRO {ma}  {"Math. Ann."}
MACRO {manu} {"Macedon. Acad. Nauk. Prilozi"}
MACRO {mcsav} {"Mat. Gasopis Sloven. Akad. Vied"}
MACRO {me}  {"Math. Education"}
MACRO {mj} {"Math. Japan"}
MACRO {mmj}  {"Michigan Math. J."}
MACRO {mm} {"Math. Mag."}
MACRO {mn} {"Math. Notes"}
MACRO {mna} {"Math. Nachr."}
MACRO {mpcps} {"Math. Proc. Cambridge Phil. Soc."}
MACRO {mpl} {"Mod. Phys. Lett."}
MACRO {ms} {"Math. Sbornik"}
MACRO {msn} {"Math. Sem. Notes"}
MACRO {msl}  {"Math. Slovak"}
MACRO {mst} {"Math. Systems Theory"}
MACRO {mz} {"Math. Z"}
MACRO {nm}  {"Numer. Math."}
MACRO {np} {"Nucl. Phys."}
MACRO {pams} {"Proc. Amer. Math. Soc."}
MACRO {pam} {"Pure Appl. Math."}
MACRO {pems} {"Proc. Edinburgh Math. Soc."}
MACRO {ph} {"Physica"}
MACRO {pim} {"Publ. Inst. Math."}
MACRO {pjm} {"Pacific J. Math."}
MACRO {pl} {"Phys. Lett."}
MACRO {plms} {"Proc. London Math. Soc."}
MACRO {pma} {"Pure Appl. Math."}
MACRO {pmd} {"Publ. Math. Debrecen"}
MACRO {pm} {"Portugal. Math"}
MACRO {pmh} {"Period Math. Hungar"}
MACRO {pmf}  {"Univ. u Novom. Sadu. Zb. Rad. Prirod.-Mat. fak."}
MACRO {pnp} {"Probl. Nucl. Phys. Cosm. Rays"}
MACRO {pr} {"Phys. Rev."}
MACRO {prl} {"Phys. Rev. Lett."}
MACRO {prse} {"Proc. Roy. Soc. Edinburgh"}
MACRO {prsl} {"Proc. Roy. Soc. London"}
MACRO {prs} {"Phys. Repts"}
MACRO {ptp} {"Progr. Theor. Phys."}
MACRO {qjm} {"Quart J. Math. Oxford"}
MACRO {qm} {"Quaestiones Math."}
MACRO {rfcuc} {"Rev. Fac. Ci. Univ. Coimbra"}
MACRO {rit}  {"RAIRO Inform Theor."}
MACRO {rmp} {"Rev. Math. Phys."}
MACRO {rms} {"Russian Math. Surv."}
MACRO {rmha} {"Rev. Mat. Hisp.-Amer. "}
MACRO {rrmpa} {"Rev. Remaine Math. Pures Appl."}
MACRO {scm} {"Stud. Cere. Mat."}
MACRO {sf} {"Semigroup Forum"}
MACRO {smj} {"Siberian Math. J."}
MACRO {smd} {"Soviet Math. Dokl."}
MACRO {ssmh} {"Studia Sci. Math. Hungar."}
MACRO {ss}  {"Simon Stevin"}
MACRO {tams} {"Trans. Amer. Math. Soc."}
MACRO {ta} {"Topology Appl."}
MACRO {tjm}  {"Tamkang J. Math."}
MACRO {tmp} {"Theor. Math. Phys."}
MACRO {tmj} {"Tohoku Math. J."}
MACRO {umj} {"Ukrainian Math. J."}
MACRO {vb}  {"Vignana Bharathi"}
MACRO {yp} {"Sov. J. Nucl. Phys."}
MACRO {zp} {"Z.~Phys."}
MACRO {uswk} {"Uniw. Slaski w Katowicach-Prace Mat."}
MACRO {beo} {"Publ. Inst. Math.(Beograd) (N. S.)"}
MACRO {asuaic} {"An.Stiint.Univ. Al.I.Cuza Iasi Sect. I a Mat.(N.S.)"}
MACRO {mflssu} {"Met. Fac. Lit. Sci. Shimane Univ. Natur. Sci."}
MACRO {mvesn} {"Mat. Vesnik"}
MACRO {sam} {"Studies in Appl. Math."}
MACRO {elm} {"Elem. Math."}
MACRO {pja} {"Proc. Japan Acad."}
MACRO {danu} {"Dokl. Akad. Nauk Ukrain SSR"}
MACRO {cmusp} {"Comment Math. Univ. St.Paul"}
MACRO {cjsm} {"Caribbean J. Sci. Math."}
MACRO {rratc} {"Res. Rep. Anan Tech. College"}
MACRO {blms} {"Bull. London Math. Soc."}
MACRO {bucms} {"Bull. Calcutta Math. Soc."}

MACRO {fp} {"Fortschr. Phys."}
MACRO {hpa} {"Helv. Phys. Acta"}

MACRO {yad} {"Ÿ¤¥à­ ï ä¨§¨ª "}
MACRO {fun} {"”ã­ªæ.  ­ «¨§ ¨ ¥£® ¯à¨«."}
MACRO {tmf} {"’¥®à. ¬ â. ä¨§."}
MACRO {umat} {"“á¯¥å¨ ¬ â. ­ ãª"}
MACRO {ufis} {"“á¯¥å¨ ä¨§. ­ ãª"}
MACRO {mza} {"Œ â. § ¬¥âª¨"}
MACRO {pzhtf} {"¨áì¬  ¢ †’”"}
MACRO {msb} {"Œ â. á¡®à­¨ª"}
MACRO {ivfiz} {"ˆ§¢. ¢ã§®¢. ”¨§¨ª "}
MACRO {ivmat} {"ˆ§¢. ¢ã§®¢. Œ â¥¬ â¨ª "}
MACRO {pyad} {"à®¡«. ï¤. ä¨§. ¨ ª®á¬. «ãç¥©"}

READ

STRINGS { longest.label }

INTEGERS { number.label longest.label.width num.multi.ref }

FUNCTION {initialize.longest.label}
{ "" 'longest.label :=
  #1 'number.label :=
  #0 'longest.label.width :=
  #0 'num.multi.ref :=
}

FUNCTION {longest.label.pass}
{ num.multi.ref duplicate$ 'multi.ref :=
  { #-1 num.multi.ref + 'num.multi.ref :=
    "" 'label :=
  }
  { number.label int.to.str$ 'label :=
    number.label #1 + 'number.label :=
    type$ "mref" =
    { cite$ #1 text.prefix$ ":" =
      { cite$ #2 #1 substring$ chr.to.int$ #-48 + 'num.multi.ref :=
      }
      'skip$
     if$
    }
    'skip$
   if$
   label width$ longest.label.width >
    { label 'longest.label :=
      label width$ 'longest.label.width :=
    }
    'skip$
   if$
  }
 if$
}

EXECUTE {initialize.longest.label}

ITERATE {longest.label.pass}

FUNCTION {begin.bib}
{ preamble$ empty$
    'skip$
    { preamble$ write$ newline$ }
  if$
  "\begin{thebibliography}{"  longest.label  * "}" * write$ newline$
}

EXECUTE {begin.bib}

EXECUTE {init.state.consts}

ITERATE {call.type$}

FUNCTION {end.bib}
{ newline$
  "\end{thebibliography}" write$ newline$
}

EXECUTE {end.bib}
