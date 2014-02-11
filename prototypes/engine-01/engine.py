#
# engine.py
#

from __future__ import with_statement
import sys, requests, json, os
from pyke import knowledge_engine, krb_traceback
#from decider import config


def start():
    """Initialize the rules engine with info from the database."""
    #krb_path = config.get('krb_path')
    krb_path = os.getenv("PWD")

    # The argument to knowledge_engine.engine() must be a path to a place
    # where the process owner can write new files to, because the compiled
    # source files will be written there.
    print "initializing engine with "+str(krb_path)
    engine = knowledge_engine.engine(krb_path)

    return engine


def getfacts(engine):
    """Load facts into the rules engine from the database."""

    # Right now we are just going to do this here, rather than from the db...
    engine.assert_('vendors', 'offering_of', ('tiny', 'att_ewr'))
    engine.assert_('vendors', 'offering_of', ('tiny', 'amz_west'))
    engine.assert_('vendors', 'offering_of', ('tiny', 'amz_east'))
    engine.assert_('vendors', 'offering_of', ('medium', 'att_ewr'))
    engine.assert_('vendors', 'offering_of', ('medium', 'hq4_user'))
    engine.assert_('vendors', 'cost_of', (8.0, 'medium', 'hq4_user'))
    engine.assert_('vendors', 'cost_of', (10.0, 'medium', 'att_ewr'))
    engine.assert_('vendors', 'cost_of', (5.0, 'tiny', 'att_ewr'))
    engine.assert_('vendors', 'cost_of', (3.0, 'tiny', 'amz_east'))
    engine.assert_('vendors', 'cost_of', (3.0, 'tiny', 'amz_west'))
    engine.assert_('vendors', 'component_runson', ('product_one', 'tiny'))
    engine.assert_('vendors', 'component_runson', ('product_two', 'tiny'))
    engine.assert_('vendors', 'component_runson', ('product_three', 'tiny'))
    engine.assert_('vendors', 'component_runson', ('product_four', 'medium'))


def getoffering(product):
    results = []

    engine = start()
    engine.reset()
    try:
        getfacts(engine)
        engine.activate('fc_components')

        with engine.prove_goal('vendors.vendor_offering_supports_forcost($vendor, $offering, '+product+', $cost)') as gen:
            for (r, p) in gen:
                results.append(r)
    except:
        krb_traceback.print_exc()
        sys.exit(1)

    return results



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: "+sys.argv[0]+" product_name"
        sys.exit(1)

    product = sys.argv[1]

    results = getoffering(product)
    if len(results) == 0:
        print "No compatible configurations were found for "+product
        sys.exit(1)

    print "Here are the results:"
    for r in results:
        print "    "+str(r)

    cheapest = results[0]
    for r in results:
        if r['cost'] < cheapest['cost']:
            cheapest = r

    print
    print "Out of the "+str(len(results))+" compatible offerings, it looks like the least"
    print "expensive compatible offering is the " \
        + str(cheapest['offering'])+" machine hosted "
    print "by "+str(cheapest['vendor'])+" for "+str(cheapest['cost'])+" buttons."


